"""
============================================
Agent1: 学习画像构建专家 (ProfileBuilderAgent)
============================================
功能：
  通过多轮对话，精准构建学习者的6维度画像，
  为后续个性化资源生成提供数据基础。

6维度画像（来自config.yaml）：
  1. knowledge_level  — 知识水平（零基础→精通）
  2. learning_style   — 学习风格（视觉/听觉/读写/实践）
  3. interest_preference — 兴趣偏好（哲学/藏象/经络/方药/诊断/养生）
  4. cognitive_ability — 认知能力（识记→评价，布鲁姆6层）
  5. learning_goal    — 学习目标（备考/考研/临床/兴趣/科研）
  6. error_prone      — 易错点识别（阴虚≠血虚混淆等）

⚠️ 免责声明：画像评估仅供教育学习参考，非医疗建议。
============================================
"""

from typing import Any, Dict, List, Optional

from crewai import Agent, Task
from loguru import logger

from app.agents.base_agent import TcmBaseAgent


class ProfileBuilderAgent(TcmBaseAgent):
    """
    学习画像构建专家

    通过对话式交互，逐步构建学习者的6维度画像。
    温度0.3，画像评估需要确定性输出，避免随意性。
    """

    agent_key = "profile_builder"
    temperature = 0.3
    needs_retriever = False  # 画像构建不需要检索
    needs_graph = False

    def create(self, **overrides) -> Agent:
        """创建画像构建专家Agent"""
        custom_backstory = overrides.pop("backstory", None) or """
你是一位资深的教育心理学专家，同时精通中医教学方法。
你擅长通过自然、轻松的对话，快速了解学习者的知识水平、学习风格和兴趣方向。

你的评估策略：
1. **暖场提问**：用中医相关的生活化问题破冰（如"你了解阴阳吗？日常有听过吗？"）
2. **深度试探**：根据回答追问细节，判断真实水平（而非表面回答）
3. **场景测试**：抛出具体的中医判断场景，观察分析能力
4. **易错点检测**：有意引导到常见混淆点，看学习者是否会踩坑

你必须输出标准的6维度画像JSON格式，每个维度都要有明确的评估值和评估依据。
不要模糊地评价，每个维度都必须有具体等级和支撑论据。
"""
        return super().create(backstory=custom_backstory, **overrides)


def create_profile_build_task(
    agent: Agent,
    user_messages: List[str],
    existing_profile: Optional[Dict] = None,
) -> Task:
    """
    创建画像构建任务

    Args:
        agent: ProfileBuilderAgent实例
        user_messages: 用户对话消息列表
        existing_profile: 已有的画像数据（用于增量更新）

    Returns:
        CrewAI Task 实例
    """
    conversation_text = "\n".join(
        f"用户: {msg}" for msg in user_messages
    )

    existing_hint = ""
    if existing_profile:
        import json
        existing_hint = f"""
## 已有画像数据（请在此基础上增量更新）：
```json
{json.dumps(existing_profile, ensure_ascii=False, indent=2)}
```
注意：如果用户的新对话没有涉及某个维度，保持原有评估不变。
"""

    description = f"""
## 任务：构建学习者的6维度画像

请根据以下对话内容，构建（或更新）学习者的6维度画像。

### 对话记录：
{conversation_text}

{existing_hint}

### 6维度画像定义（必须全部评估）：

1. **knowledge_level（知识水平）**
   - 零基础 / 初步了解 / 基本掌握 / 熟练掌握 / 精通
   - 评估依据：从对话中判断对中医基础概念的掌握程度

2. **learning_style（学习风格）**
   - 视觉型(图表/导图) / 听觉型(讲解/讨论) / 读写型(文档/笔记) / 实践型(案例/操作)
   - 评估依据：用户提问方式、表达偏好

3. **interest_preference（兴趣偏好）**
   - 可多选：哲学基础 / 藏象理论 / 经络针灸 / 方药应用 / 诊断实践 / 养生保健
   - 评估依据：用户主动询问的方向

4. **cognitive_ability（认知能力）**
   - 识记 / 理解 / 应用 / 分析 / 综合 / 评价（布鲁姆分类）
   - 评估依据：用户能否进行推理、对比、综合判断

5. **learning_goal（学习目标）**
   - 期末备考 / 考研复习 / 临床衔接 / 兴趣拓展 / 科研入门
   - 评估依据：用户明确表述或隐含的意图

6. **error_prone（易错点识别）**
   - 列出学习者容易混淆的概念（如阴虚≠血虚）
   - 评估依据：对话中出现的误解或混淆

### 输出格式（严格JSON）：

```json
{{
  "knowledge_level": {{"value": "基本掌握", "evidence": "用户能正确解释阴阳基本概念，但对五行相生相克理解有误"}},
  "learning_style": {{"value": "视觉型", "evidence": "用户多次要求图表和思维导图形式呈现"}},
  "interest_preference": {{"value": ["藏象理论", "经络针灸"], "evidence": "用户主动询问肝的功能和经络走向"}},
  "cognitive_ability": {{"value": "应用", "evidence": "用户能将阴阳理论应用到具体案例分析"}},
  "learning_goal": {{"value": "期末备考", "evidence": "用户明确表示正在准备中医基础理论期末考试"}},
  "error_prone": {{"value": ["阴虚与血虚混淆", "风寒与风热鉴别不清"], "evidence": "用户在案例判断中将阴虚误判为血虚"}},
  "profile_confidence": 0.85,
  "needs_more_info": false,
  "suggested_questions": []
}}
```

如果对话轮数不足，某些维度无法判断，请将 needs_more_info 设为 true，
并在 suggested_questions 中给出建议的后续提问。

⚠️ 画像评估仅供教育学习参考，非医疗建议。
"""

    expected_output = (
        "一份完整的6维度学习画像JSON，每个维度包含value（评估值）和evidence（评估依据），"
        "以及整体置信度profile_confidence和是否需要更多信息needs_more_info。"
    )

    return Task(
        description=description,
        agent=agent,
        expected_output=expected_output,
    )
