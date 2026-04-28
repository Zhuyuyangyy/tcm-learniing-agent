"""
============================================
统一数据模型（Pydantic Schemas）
============================================
定义所有API请求/响应体、学习画像、资源、Agent日志等数据结构。

⚠️ 免责声明：所有数据仅供教育学习参考，非医疗建议。
============================================
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================
# 枚举类型
# ============================================================

class TaskType(str, Enum):
    """任务类型"""
    BUILD_PROFILE = "build_profile"
    GENERATE_RESOURCES = "generate_resources"
    PLAN_LEARNING_PATH = "plan_learning_path"


class KnowledgeLevel(str, Enum):
    """知识水平"""
    ZERO = "零基础"
    BEGINNER = "初步了解"
    BASIC = "基本掌握"
    PROFICIENT = "熟练掌握"
    EXPERT = "精通"


class LearningStyle(str, Enum):
    """学习风格"""
    VISUAL = "视觉型(图表/导图)"
    AUDITORY = "听觉型(讲解/讨论)"
    READ_WRITE = "读写型(文档/笔记)"
    KINESTHETIC = "实践型(案例/操作)"


class CognitiveLevel(str, Enum):
    """认知能力层级（布鲁姆分类）"""
    REMEMBER = "识记"
    UNDERSTAND = "理解"
    APPLY = "应用"
    ANALYZE = "分析"
    EVALUATE = "综合"
    CREATE = "评价"


class LearningGoal(str, Enum):
    """学习目标"""
    EXAM = "期末备考"
    POSTGRAD = "考研复习"
    CLINICAL = "临床衔接"
    INTEREST = "兴趣拓展"
    RESEARCH = "科研入门"


class ResourceType(str, Enum):
    """资源类型"""
    LECTURE_DOC = "lecture_doc"
    MIND_MAP = "mind_map"
    QUIZ_BANK = "quiz_bank"
    EXTENDED_READING = "extended_reading"
    ANIMATION_DESC = "animation_desc"
    PRACTICE_CASE = "practice_case"


class CritiqueVerdict(str, Enum):
    """审校结论"""
    APPROVE = "APPROVE"
    WARN = "WARN"
    REJECT = "REJECT"


class CrewStatus(str, Enum):
    """Crew执行状态"""
    IDLE = "idle"
    BUILDING_PROFILE = "building_profile"
    RETRIEVING = "retrieving"
    GENERATING = "generating"
    CRITIQUING = "critiquing"
    PLANNING_PATH = "planning_path"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================
# 学习画像模型
# ============================================================

class DimensionAssessment(BaseModel):
    """单维度评估结果"""
    value: Any = Field(description="评估值")
    evidence: str = Field(default="", description="评估依据")

class UserProfile(BaseModel):
    """
    学习者6维度画像

    每个维度包含 value（评估值）和 evidence（评估依据），
    确保画像的可解释性。
    """
    knowledge_level: DimensionAssessment = Field(
        default=DimensionAssessment(value=KnowledgeLevel.ZERO, evidence=""),
        description="知识水平评估"
    )
    learning_style: DimensionAssessment = Field(
        default=DimensionAssessment(value=LearningStyle.VISUAL, evidence=""),
        description="学习风格评估"
    )
    interest_preference: DimensionAssessment = Field(
        default=DimensionAssessment(value=[], evidence=""),
        description="兴趣偏好评估"
    )
    cognitive_ability: DimensionAssessment = Field(
        default=DimensionAssessment(value=CognitiveLevel.UNDERSTAND, evidence=""),
        description="认知能力评估"
    )
    learning_goal: DimensionAssessment = Field(
        default=DimensionAssessment(value=LearningGoal.INTEREST, evidence=""),
        description="学习目标评估"
    )
    error_prone: DimensionAssessment = Field(
        default=DimensionAssessment(value=[], evidence=""),
        description="易错点识别"
    )
    profile_confidence: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="画像整体置信度"
    )
    needs_more_info: bool = Field(
        default=True,
        description="是否需要更多对话来完善画像"
    )
    suggested_questions: List[str] = Field(
        default_factory=list,
        description="建议的后续提问"
    )


# ============================================================
# Agent交互日志模型
# ============================================================

class AgentLog(BaseModel):
    """
    智能体交互日志

    记录每个Agent的执行过程，用于：
    1. 前端"Agent工作台"动画展示
    2. 调试和问题排查
    3. 演示视频素材
    """
    agent_name: str = Field(description="Agent名称（如profile_builder, critique_agent）")
    agent_role: str = Field(description="Agent角色（如中医知识检索专家）")
    step: str = Field(description="执行步骤标识")
    input_summary: str = Field(default="", description="输入摘要")
    output_summary: str = Field(default="", description="输出摘要")
    status: CrewStatus = Field(description="执行状态")
    verdict: Optional[CritiqueVerdict] = Field(default=None, description="审校结论（仅critique_agent）")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    duration_ms: Optional[int] = Field(default=None, description="执行耗时（毫秒）")
    error: Optional[str] = Field(default=None, description="错误信息")


# ============================================================
# 资源响应模型
# ============================================================

class ResourceItem(BaseModel):
    """单个资源项"""
    type: ResourceType = Field(description="资源类型")
    format: str = Field(description="输出格式（markdown/json）")
    content: Any = Field(description="资源内容")

class ResourceResponse(BaseModel):
    """
    最终资源响应体

    包含完整的执行结果：画像、检索报告、资源包、审校报告、学习路径。
    """
    # 基础信息
    task_type: TaskType = Field(description="任务类型")
    status: CrewStatus = Field(description="执行状态")

    # Step1: 画像
    profile: Optional[UserProfile] = Field(default=None, description="学习者画像")

    # Step2: 检索
    retrieval_report: Optional[str] = Field(default=None, description="检索报告摘要")

    # Step3: 资源
    resources: Optional[Dict[str, Any]] = Field(default=None, description="资源包")

    # Step4: 审校
    critique_report: Optional[str] = Field(default=None, description="审校报告")
    critique_verdict: Optional[CritiqueVerdict] = Field(default=None, description="审校结论")

    # Step5: 路径
    learning_path: Optional[Dict[str, Any]] = Field(default=None, description="学习路径")

    # 元数据
    agent_logs: List[AgentLog] = Field(default_factory=list, description="Agent交互日志")
    retry_count: int = Field(default=0, description="审校重试次数")
    errors: List[str] = Field(default_factory=list, description="错误信息")
    disclaimer: str = Field(
        default="⚠️ 本内容由AI生成，基于中医教材知识库检索，仅供教育学习参考，非医疗建议。如有健康问题请咨询专业中医师。",
        description="免责声明"
    )
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================
# API请求模型
# ============================================================

class LearningRequest(BaseModel):
    """
    /api/v1/chat/learning 接口请求体

    支持三种任务类型：
      - build_profile: 仅构建画像
      - generate_resources: 生成资源（默认）
      - plan_learning_path: 规划路径
    """
    user_messages: List[str] = Field(
        description="用户对话消息列表（支持多轮对话）",
        examples=[["我想学中医基础理论，特别是阴阳五行方面的内容"]]
    )
    task_type: TaskType = Field(
        default=TaskType.GENERATE_RESOURCES,
        description="任务类型"
    )
    profile_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="已有画像数据（增量更新用）"
    )
    knowledge_point: Optional[str] = Field(
        default=None,
        description="指定知识点（如不指定则根据画像自动推断）"
    )
    resource_types: Optional[List[ResourceType]] = Field(
        default=None,
        description="指定资源类型（如不指定则生成全部类型）"
    )


class SSEEvent(BaseModel):
    """SSE事件格式（用于流式推送Agent中间过程）"""
    event: str = Field(description="事件类型（step/result/error）")
    data: Dict[str, Any] = Field(description="事件数据")
    timestamp: datetime = Field(default_factory=datetime.now)
