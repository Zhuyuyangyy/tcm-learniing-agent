"""
============================================
Agent2: 中医知识检索专家 (TcmRetrieverAgent)
============================================
功能：
  从中医知识库中精准检索与学习者画像匹配的知识点，
  确保所有生成内容有据可依。是防幻觉的第一道关卡。

核心能力：
  - 混合检索：向量相似度 + 关键词匹配 + 知识图谱交叉验证
  - 章节定位：自动映射到教材章节路径
  - 语义扩展：将模糊查询扩展为精确的中医术语检索

⚠️ 基于讯飞星火 v3.5/4.0 驱动的知识检索
⚠️ 免责声明：所有检索内容仅供教育学习参考，非医疗建议。
============================================
"""

from typing import Any, List

from crewai import Agent, Task
from loguru import logger

from app.agents.base_agent import TcmBaseAgent


class TcmRetrieverAgent(TcmBaseAgent):
    """
    中医知识检索专家

    专注从RAG知识库和知识图谱中提取原始知识，
    为后续的资源生成Agent提供可靠的素材基础。

    温度设置为0.2，追求检索查询的精确性，
    避免因创意发挥而偏离用户实际需求。
    """

    agent_key = "tcm_retriever"
    temperature = 0.2  # 检索需要高度确定性
    needs_retriever = True  # 需要向量检索工具
    needs_graph = True  # 需要知识图谱工具

    def create(self, **overrides) -> Agent:
        """
        创建中医知识检索专家Agent

        role: "中医知识检索专家"
        goal: 精准检索，确保所有生成内容有据可依
        backstory: 精通中医文献和现代教材体系的文献学专家
        """
        return super().create(**overrides)


# ============================================================
# 检索任务定义
# ============================================================

def create_retrieval_task(agent: Agent, query: str, profile_context: str = "") -> Task:
    """
    创建知识检索任务

    Args:
        agent: TcmRetrieverAgent实例
        query: 检索查询（来自用户问题或画像分析结果）
        profile_context: 学习画像上下文（用于个性化检索）

    Returns:
        CrewAI Task 实例
    """
    profile_hint = ""
    if profile_context:
        profile_hint = f"""
学习者画像参考：
{profile_context}

请根据以上画像信息，调整检索策略和结果排序。
例如：初学者优先检索基础概念，进阶者优先检索临床应用和鉴别诊断。
"""

    description = f"""
## 任务：中医知识精准检索

请从中医基础理论知识库中，检索以下问题的相关内容：

**检索问题**：{query}

{profile_hint}

## 检索要求：

1. **全面性**：使用向量检索和知识图谱两种方式交叉验证
2. **准确性**：优先返回教材原文表述，而非AI改写版本
3. **层级性**：标注检索结果的章节来源路径
4. **相关性**：如果检索结果不够相关，请使用不同的关键词重新检索

## 输出格式：

请按以下格式整理检索结果：

```
【检索主题】{query}
【检索来源】向量检索 + 知识图谱交叉验证
【检索结果】
  1. [章节路径] 相关内容摘要...
  2. [章节路径] 相关内容摘要...
  ...
【知识图谱验证】
  - 实体A → [关系] → 实体B ✓
  - 实体C → [关系] → 实体D ✓
【检索置信度】高/中/低
```

⚠️ 所有内容仅供教育学习参考，非医疗建议。
"""

    expected_output = (
        "一份结构化的中医知识检索报告，包含："
        "1) 至少3条相关教材原文；"
        "2) 知识图谱验证结果；"
        "3) 检索置信度评估。"
        "所有内容必须来源于知识库检索，不可凭空编造。"
    )

    return Task(
        description=description,
        agent=agent,
        expected_output=expected_output,
    )
