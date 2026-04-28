"""
============================================
中医学习多智能体编排引擎（赛题"多智能体协同"计分核心）
============================================
功能：
  定义完整的 Task 链和 Crew 流程：
    画像构建 → 知识检索 → 资源生成 → 老中医审校

核心机制：
  1. 闭环反馈：如果 critique_agent 输出 [REJECT]，流程回退到资源生成重新执行
  2. 最多重试 2 次，超过则标记为"需人工审核"返回前端
  3. 每步 Agent 输出都会通过 SSE 实时推送到前端
  4. 所有流程以"防幻觉"和"个性化生成"为主轴

数据流交接说明（中文详注）：
  Step1: 用户对话 → ProfileBuilder → 输出 UserProfile JSON
  Step2: UserProfile + 用户问题 → TcmRetriever → 输出 检索报告
  Step3: UserProfile + 检索报告 → ResourceGenerator → 输出 资源包JSON
  Step4: 资源包JSON + 检索报告 → CritiqueAgent → 输出 审校报告
  Step5: 如果 [REJECT] → 回退 Step3 重新生成（附加审校反馈）
  Step6: 如果 [APPROVE] → PathPlanner → 输出 学习路径JSON

⚠️ 基于讯飞星火 v3.5/4.0 驱动的多智能体协同
⚠️ 免责声明：所有输出仅供教育学习参考，非医疗建议
============================================
"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from crewai import Agent, Crew, Process, Task
from loguru import logger

# 业务埋点日志函数
from app.core.logger import (
    logger as _logger,
    log_agent_task_received,
    log_agent_task_completed,
    log_critique_reject,
    log_state_transition,
)

# 延迟导入避免循环依赖，所有Task创建函数在运行时按需导入


# ============================================================
# 流程状态枚举
# ============================================================

class CrewState(str, Enum):
    """Crew执行状态"""
    IDLE = "idle"
    BUILDING_PROFILE = "building_profile"      # Step1: 画像构建中
    RETRIEVING = "retrieving"                    # Step2: 知识检索中
    GENERATING = "generating"                    # Step3: 资源生成中
    CRITIQUING = "critiquing"                    # Step4: 老中医审校中
    PLANNING_PATH = "planning_path"              # Step6: 路径规划中
    RETRYING = "retrying"                        # Step5: 审校未通过，回退重试
    COMPLETED = "completed"                      # 完成
    FAILED = "failed"                            # 失败（超过重试上限）


# ============================================================
# 核心编排类
# ============================================================

class TcmLearningCrew:
    """
    中医学习多智能体编排引擎

    这是整个系统的"大脑"，负责协调6个Agent的工作流程。

    编排逻辑：
      ┌─────────────┐
      │  用户输入    │
      └──────┬──────┘
             ▼
      ┌─────────────┐    Step1: 对话→画像
      │ProfileBuilder│
      └──────┬──────┘
             ▼ UserProfile
      ┌─────────────┐    Step2: 画像+问题→检索
      │TcmRetriever │
      └──────┬──────┘
             ▼ 检索报告
      ┌─────────────┐    Step3: 画像+检索→资源
      │ResourceGen  │◄─────────────────┐
      └──────┬──────┘                   │
             ▼ 资源包                    │
      ┌─────────────┐    Step4: 资源+检索→审校 │
      │CritiqueAgent │                   │
      └──────┬──────┘                   │
             │                          │
        [APPROVE]?                     │
         Yes ↓    No → [REJECT] ───────┘
      ┌─────────────┐    Step6: 画像+进度→路径
      │PathPlanner  │
      └──────┬──────┘
             ▼
      ┌─────────────┐
      │  最终输出    │
      └─────────────┘

    使用示例：
        >>> crew = TcmLearningCrew()
        >>> result = await crew.run(
        ...     user_messages=["我想学中医基础理论"],
        ...     task_type="generate_resources",
        ...     on_step_callback=print  # SSE推送用
        ... )
    """

    # 最大审校重试次数
    MAX_CRITIQUE_RETRIES = 2

    def __init__(self):
        """初始化所有Agent实例"""
        # Step1: 画像构建专家
        self.profile_builder = ProfileBuilderAgent().create()
        # Step2: 中医知识检索专家
        self.tcm_retriever = TcmRetrieverAgent().create()
        # Step3: 资源生成专家
        self.resource_generator = ResourceGeneratorAgent().create()
        # Step4: 杏林纠错官（防幻觉核心）
        self.critique_agent = CritiqueAgent().create()
        # Step6: 路径规划专家
        self.path_planner = PathPlannerAgent().create()

        self.state = CrewState.IDLE
        self._step_callbacks: List[Callable] = []

        logger.info("✅ TcmLearningCrew 初始化完成 | 6个Agent就绪")

    def on_step(self, callback: Callable):
        """
        注册步骤回调（用于SSE推送）

        每个Agent完成一步后，会调用回调函数，
        将中间结果和"思考过程"推送到前端。

        回调签名：callback(step_name, step_data, state, detailed_log=None)
        """
        self._step_callbacks.append(callback)

    async def _emit_step(self, step_name: str, step_data: Any, state: CrewState, detailed_log: Optional[Dict] = None):
        """触发步骤回调，附带详细日志"""
        self.state = state
        for cb in self._step_callbacks:
            try:
                # 兼容新旧回调签名
                import inspect
                sig = inspect.signature(cb)
                if len(sig.parameters) >= 4:
                    cb(step_name, step_data, state.value, detailed_log)
                else:
                    cb(step_name, step_data, state.value)
            except Exception as e:
                logger.warning(f"步骤回调异常: {e}")

    # ============================================================
    # 主流程入口
    # ============================================================

    async def run(
        self,
        user_messages: List[str],
        task_type: str = "generate_resources",
        profile_data: Optional[Dict] = None,
        knowledge_point: str = "",
        resource_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        执行完整的多智能体学习流程

        Args:
            user_messages: 用户对话消息列表
            task_type: 任务类型
                - "build_profile": 仅构建画像
                - "generate_resources": 生成资源（默认）
                - "plan_learning_path": 规划学习路径
            profile_data: 已有画像（增量更新用）
            knowledge_point: 指定知识点
            resource_types: 指定资源类型

        Returns:
            完整结果字典，包含画像、资源、审校报告、学习路径
        """
        result = {
            "task_type": task_type,
            "state": CrewState.IDLE.value,
            "profile": None,
            "retrieval_report": None,
            "resources": None,
            "critique_report": None,
            "learning_path": None,
            "retry_count": 0,
            "errors": [],
        }

        # 延迟导入所有Task创建函数（避免循环依赖）
        from app.agents.profile_builder import ProfileBuilderAgent as _PBA, create_profile_build_task
        from app.agents.tcm_retriever import TcmRetrieverAgent as _TRA, create_retrieval_task
        from app.agents.resource_generator import ResourceGeneratorAgent as _RGA, create_resource_generation_task
        from app.agents.critique_agent import CritiqueAgent as _CA, create_critique_task
        from app.agents.path_planner import PathPlannerAgent as _PPA, create_path_planning_task

        try:
            # ============================================================
            # Step1: 画像构建
            # ProfileBuilder 分析用户对话，输出6维度画像
            # 数据交接：用户对话 → ProfileBuilder → UserProfile JSON
            # ============================================================
            await self._emit_step("profile_building", "开始构建学习画像...", CrewState.BUILDING_PROFILE,
                detailed_log={"thought": "分析用户对话内容，提取知识水平、学习风格等6维度信号...", "agent": "ProfileBuilder"})

            profile_task = create_profile_build_task(
                agent=self.profile_builder,
                user_messages=user_messages,
                existing_profile=profile_data,
            )

            profile_crew = Crew(
                agents=[self.profile_builder],
                tasks=[profile_task],
                verbose=True,
                process=Process.sequential,
            )

            profile_result = profile_crew.kickoff()
            result["profile"] = self._parse_agent_output(profile_result, "profile")

            # ---- Agent 追踪埋点：画像构建完成 ----
            log_agent_task_completed(
                agent_name="ProfileBuilder",
                task_type="build_profile",
                output_preview=str(result["profile"])[:80] if result["profile"] else "",
            )

            # 预先计算置信度（避免 Python 3.12 f-string 嵌套引号问题）
            _profile_conf = (result["profile"].get("profile_confidence", "?") if isinstance(result.get("profile"), dict) else "?")
            await self._emit_step("profile_built", result["profile"], CrewState.BUILDING_PROFILE,
                detailed_log={"thought": f"画像构建完成，置信度={_profile_conf}", "agent": "ProfileBuilder"})

            # 如果只是构建画像，到此结束
            if task_type == "build_profile":
                result["state"] = CrewState.COMPLETED.value
                return result

            # ============================================================
            # Step2: 知识检索
            # TcmRetriever 根据画像和用户问题检索知识库
            # 数据交接：UserProfile + 用户问题 → TcmRetriever → 检索报告
            # ============================================================
            await self._emit_step("retrieving", "正在检索中医知识库...", CrewState.RETRIEVING,
                detailed_log={"thought": f"从画像提取检索关键词: {query}", "agent": "TcmRetriever"})

            # 从画像中提取检索关键词
            query = knowledge_point or self._extract_query_from_profile(result["profile"])

            retrieval_task = create_retrieval_task(
                agent=self.tcm_retriever,
                query=query,
                profile_context=json.dumps(result["profile"], ensure_ascii=False) if result["profile"] else "",
            )

            retrieval_crew = Crew(
                agents=[self.tcm_retriever],
                tasks=[retrieval_task],
                verbose=True,
                process=Process.sequential,
            )

            retrieval_result = retrieval_crew.kickoff()
            result["retrieval_report"] = self._parse_agent_output(retrieval_result, "retrieval")

            # ---- Agent 追踪埋点：检索完成 ----
            log_agent_task_completed(
                agent_name="TcmRetriever",
                task_type="retrieve_knowledge",
                output_preview=str(result["retrieval_report"])[:80] if result["retrieval_report"] else "",
            )

            await self._emit_step("retrieved", result["retrieval_report"], CrewState.RETRIEVING,
                detailed_log={"thought": "检索完成，正在交叉验证图谱三元组...", "agent": "TcmRetriever"})

            # 如果只是规划路径，跳过资源生成和审校
            if task_type == "plan_learning_path":
                # 直接进入路径规划
                await self._run_path_planning(result)
                result["state"] = CrewState.COMPLETED.value
                return result

            # ============================================================
            # Step3 + Step4: 资源生成 + 审校（含重试循环）
            #
            # 核心闭环逻辑：
            #   ResourceGenerator 生成资源 → CritiqueAgent 审校
            #   → 如果 [REJECT]，将审校反馈附加到下一次生成的Prompt中
            #   → 重新执行 ResourceGenerator
            #   → 最多重试 MAX_CRITIQUE_RETRIES 次
            # ============================================================
            critique_feedback = ""  # 审校反馈（首次为空）

            for attempt in range(self.MAX_CRITIQUE_RETRIES + 1):
                # ---- Step3: 资源生成 ----
                # 数据交接：UserProfile + 检索报告 + 审校反馈(如有) → ResourceGenerator → 资源包JSON
                step_label = f"资源生成（第{attempt+1}次）" if attempt > 0 else "资源生成"
                await self._emit_step("generating", f"正在{step_label}...", CrewState.GENERATING,
                    detailed_log={"thought": f"根据画像和检索结果，选择最优资源类型组合进行生成...（第{attempt+1}次）", "agent": "ResourceGenerator", "attempt": attempt+1})

                resource_task = create_resource_generation_task(
                    agent=self.resource_generator,
                    profile_data=result["profile"] or {},
                    retrieval_results=result["retrieval_report"] or "",
                    resource_types=resource_types,
                    knowledge_point=knowledge_point,
                )

                # 如果有审校反馈，附加到任务描述中（指导Agent修正）
                if critique_feedback:
                    resource_task.description += f"""

## ⚠️ 上次审校反馈（请据此修正）：
{critique_feedback}

请特别注意修正上述问题，确保这次生成的内容能通过审校。
"""

                resource_crew = Crew(
                    agents=[self.resource_generator],
                    tasks=[resource_task],
                    verbose=True,
                    process=Process.sequential,
                )

                resource_result = resource_crew.kickoff()
                result["resources"] = self._parse_agent_output(resource_result, "resources")  # 修复: 变量名resource_result

                await self._emit_step("generated", result["resources"], CrewState.GENERATING,
                    detailed_log={"thought": "资源生成完成，准备提交审校...", "agent": "ResourceGenerator"})

                # ---- Step4: 老中医审校 ----
                # 数据交接：资源包JSON + 检索报告 → CritiqueAgent → 审校报告([APPROVE/WARN/REJECT])
                await self._emit_step("critiquing", "杏林纠错官正在审校...", CrewState.CRITIQUING,
                    detailed_log={"thought": "老夫逐条审查生成内容，与图谱三元组对比验证...", "agent": "CritiqueAgent(杏林纠错官)"})

                content_type = "个性化学习资源包"
                critique_task = create_critique_task(
                    agent=self.critique_agent,
                    content_to_review=result["resources"] or "",
                    retrieval_sources=result["retrieval_report"] or "",
                    content_type=content_type,
                )

                critique_crew = Crew(
                    agents=[self.critique_agent],
                    tasks=[critique_task],
                    verbose=True,
                    process=Process.sequential,
                )

                critique_result = critique_crew.kickoff()
                result["critique_report"] = self._parse_agent_output(critique_result, "critique")

                await self._emit_step("critiqued", result["critique_report"], CrewState.CRITIQUING,
                    detailed_log={"thought": f"审校完毕，结论: {'通过' if '[APPROVE]' in critique_text else '需修正' if '[WARN]' in critique_text else '拒绝'}", "agent": "CritiqueAgent(杏林纠错官)"})

                # ---- 判定审校结果 ----
                critique_text = str(result["critique_report"] or "")

                if "[REJECT]" in critique_text:
                    # 审校未通过 → 提取反馈 → 重试
                    result["retry_count"] = attempt + 1
                    critique_feedback = critique_text

                    # ---- 拦截记录埋点：REJECT 必须详细记录 ----
                    _reject_reason = self._extract_reject_reason(critique_text)
                    _hallucination_content = self._extract_rejected_claims(critique_text)
                    _suggested_fix = self._extract_suggested_fix(critique_text)
                    
                    log_critique_reject(
                        hallucination_content=_hallucination_content or str(result["resources"])[:150],
                        reject_reason=_reject_reason or "知识图谱验证失败",
                        confidence=0.1,  # REJECT 通常低置信度
                        suggested_fix=_suggested_fix,
                    )
                    
                    logger.warning(
                        f"🚫 杏林纠错官 [REJECT] | 第{attempt+1}次审校未通过，"
                        f"{'准备重试' if attempt < self.MAX_CRITIQUE_RETRIES else '已达重试上限'}"
                    )

                    await self._emit_step(
                        "retry",
                        f"审校未通过，第{attempt+1}次重试...",
                        CrewState.RETRYING,
                        detailed_log={"thought": "杏林纠错官拒绝，将审校反馈注入重新生成...", "agent": "Coordinator", "retry": attempt+1},
                    )

                    if attempt >= self.MAX_CRITIQUE_RETRIES:
                        # 超过重试上限 → 标记为需人工审核
                        result["errors"].append(
                            "审校多次未通过，生成内容可能存在不准确之处，建议人工审核"
                        )
                        result["state"] = CrewState.FAILED.value
                        return result

                    continue  # 重试

                elif "[WARN]" in critique_text:
                    # 有警告但通过 → 标记并继续
                    logger.info("⚠️ 杏林纠错官 [WARN] | 审校有警告但通过")
                    result["state"] = CrewState.COMPLETED.value
                    break

                else:
                    # [APPROVE] 或无特殊标记 → 通过
                    logger.info("✅ 杏林纠错官 [APPROVE] | 审校通过")
                    result["state"] = CrewState.COMPLETED.value
                    break

            # ============================================================
            # Step6: 学习路径规划（资源审校通过后）
            # 数据交接：UserProfile + 学习进度 → PathPlanner → 学习路径JSON
            # ============================================================
            await self._run_path_planning(result)

            result["state"] = CrewState.COMPLETED.value

        except Exception as e:
            logger.error(f"❌ Crew执行异常: {e}")
            result["state"] = CrewState.FAILED.value
            result["errors"].append(str(e))

        return result

    # ============================================================
    # 辅助方法
    # ============================================================

    async def _run_path_planning(self, result: Dict[str, Any]):
        """执行学习路径规划"""
        await self._emit_step("planning_path", "正在规划个性化学习路径...", CrewState.PLANNING_PATH,
            detailed_log={"thought": "根据画像掌握度和认知负荷，动态调整学习节点顺序...", "agent": "PathPlanner"})

        path_task = create_path_planning_task(
            agent=self.path_planner,
            profile_data=result.get("profile") or {},
        )

        path_crew = Crew(
            agents=[self.path_planner],
            tasks=[path_task],
            verbose=True,
            process=Process.sequential,
        )

        path_result = path_crew.kickoff()
        result["learning_path"] = self._parse_agent_output(path_result, "path")

        await self._emit_step("path_planned", result["learning_path"], CrewState.PLANNING_PATH,
            detailed_log={"thought": "学习路径规划完成，含前置依赖和复习节点", "agent": "PathPlanner"})

    def _parse_agent_output(self, crew_output, label: str) -> Any:
        """
        解析CrewAI的输出结果

        CrewAI的kickoff()返回一个CrewOutput对象，
        需要提取其中的文本内容并尝试解析为JSON。

        Args:
            crew_output: CrewAI输出对象
            label: 标签（用于日志）

        Returns:
            解析后的内容（JSON dict 或 纯文本）
        """
        # CrewAI输出可能是字符串或对象
        raw = str(crew_output)

        # 尝试提取JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', raw, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试直接解析整个输出为JSON
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # 返回原始文本
        return raw

    def _extract_query_from_profile(self, profile: Any) -> str:
        """
        从学习者画像中提取检索关键词

        根据画像的兴趣偏好和易错点，
        生成最适合的检索查询。
        """
        if isinstance(profile, dict):
            # 提取兴趣偏好
            interests = profile.get("interest_preference", {})
            interest_val = interests.get("value", [])
            if isinstance(interest_val, list):
                query = "、".join(interest_val[:3])
            else:
                query = str(interest_val)

            # 附加易错点
            errors = profile.get("error_prone", {})
            error_val = errors.get("value", [])
            if error_val:
                if isinstance(error_val, list):
                    query += " " + " ".join(error_val[:2])

            return query or "中医基础理论概述"

        return "中医基础理论概述"

    def _extract_reject_reason(self, critique_text: str) -> str:
        """
        从审校文本中提取拒绝原因
        
        解析审校报告，提取 "🚫 拒绝项" 部分的详细内容。
        """
        # 匹配 "🚫 拒绝项:" 或 "🚫 拒绝项" 之后的内容
        reject_match = re.search(r'[🚫❌]\s*拒绝项[:：]\s*(.*?)(?=\n\n|\n【|$)', critique_text, re.DOTALL)
        if reject_match:
            reason = reject_match.group(1).strip()
            # 取前100字
            return reason[:100]
        
        # 备用：从"老夫点评"中提取
        comment_match = re.search(r'老夫点评[:：]\s*(.*?)(?=\n|\【|$)', critique_text, re.DOTALL)
        if comment_match:
            return comment_match.group(1).strip()[:100]
        
        return ""

    def _extract_rejected_claims(self, critique_text: str) -> str:
        """
        从审校文本中提取被拒绝的具体断言
        
        用于日志记录拦截的幻觉内容。
        """
        # 匹配被拒绝的断言列表
        claims_match = re.search(r'拒绝项[:：]\s*(.*?)(?=\n\n|\n【|修正建议|$)', critique_text, re.DOTALL)
        if claims_match:
            claims = claims_match.group(1).strip()
            # 清理格式，取前150字
            claims = re.sub(r'\n\s*[-*]', ' | ', claims)
            return claims[:150]
        return ""

    def _extract_suggested_fix(self, critique_text: str) -> str:
        """
        从审校文本中提取修正建议
        """
        fix_match = re.search(r'修正建议[:：]\s*(.*?)(?=\n\n|\n【|免责声明|$)', critique_text, re.DOTALL)
        if fix_match:
            fix = fix_match.group(1).strip()
            return fix[:120]
        return ""
