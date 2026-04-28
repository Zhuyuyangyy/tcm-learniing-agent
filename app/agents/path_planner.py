"""
============================================
Agent4: 个性化学习路径规划专家 (PathPlannerAgent)
============================================
功能：
  根据学习画像的"掌握度"和"认知负荷"，
  动态调整《中医基础理论》的下一步学习节点。

核心能力：
  - 基于布鲁姆认知分类法安排学习递进
  - 考虑知识点之间的前置依赖关系（如：先学阴阳再学藏象）
  - 适配学习者的时间约束和负荷承受能力
  - 自动安排复习节点（艾宾浩斯遗忘曲线）

⚠️ 免责声明：学习路径仅供教育参考，非医疗建议。
============================================
"""

from typing import Any, Dict, List, Optional

from crewai import Agent, Task
from loguru import logger

from app.agents.base_agent import TcmBaseAgent


class PathPlannerAgent(TcmBaseAgent):
    """
    个性化学习路径规划专家

    根据画像数据和学习目标，动态规划最优学习路径。
    温度0.4，路径规划需要逻辑性，但也要适当灵活性。
    """

    agent_key = "path_planner"
    temperature = 0.4
    needs_retriever = True  # 需要检索课程大纲内容
    needs_graph = False

    def create(self, **overrides) -> Agent:
        """创建路径规划专家Agent"""
        custom_backstory = overrides.pop("backstory", None) or """
你是一位教学设计专家，精通布鲁姆认知分类法和中医课程体系。

你规划学习路径的核心理念：
1. **循序渐进**：中医知识有严格的前置依赖（不懂阴阳，何以懂藏象？不懂藏象，何以懂病机？）
2. **因材施教**：零基础者从哲学基础开始，有基础者直接进入薄弱章节
3. **认知递进**：识记→理解→应用→分析，每个知识点都按认知层次递进
4. **间隔复习**：根据艾宾浩斯遗忘曲线安排复习节点

你输出的学习路径必须包含：
  - 明确的学习阶段划分
  - 每个阶段的预计学习时长
  - 知识点之间的前置依赖关系
  - 阶段性检测点（学完一章后自测）
  - 薄弱点强化计划
"""
        return super().create(backstory=custom_backstory, **overrides)


def create_path_planning_task(
    agent: Agent,
    profile_data: Dict[str, Any],
    course_progress: Optional[Dict] = None,
) -> Task:
    """
    创建学习路径规划任务

    Args:
        agent: PathPlannerAgent实例
        profile_data: 学习者6维度画像数据
        course_progress: 已完成的学习进度

    Returns:
        CrewAI Task 实例
    """
    import json
    profile_text = json.dumps(profile_data, ensure_ascii=False, indent=2)

    progress_hint = ""
    if course_progress:
        progress_hint = f"""
## 已有学习进度：
{json.dumps(course_progress, ensure_ascii=False, indent=2)}
请基于已完成的进度继续规划，避免重复已学内容。
"""

    description = f"""
## 任务：规划个性化学习路径

请根据以下学习者画像，规划《中医基础理论》的个性化学习路径。

### 学习者画像：
{profile_text}

{progress_hint}

### 课程大纲（7章）：
1. 中医学的哲学基础（阴阳、五行、精气学说）
2. 藏象学说（五脏六腑、奇恒之腑）
3. 气血津液
4. 经络学说
5. 病因（六淫、七情等）
6. 病机
7. 防治原则

### 规划要求：

1. **前置依赖**：
   - 第1章（哲学基础）是所有后续章节的前提
   - 第2章（藏象）是第3章（气血津液）的前提
   - 第5章（病因）是第6章（病机）的前提
   - 第7章（防治）需要前6章基础

2. **个性化调整**：
   - 根据knowledge_level决定起点和速度
   - 根据error_prone安排强化训练节点
   - 根据learning_goal调整深度（备考侧重重点，兴趣拓展侧重广度）
   - 根据learning_style适配资源类型建议

3. **认知递进**：
   - 每个知识点按 识记→理解→应用 三层递进
   - 标注每层的建议学习时长

### 输出格式（JSON）：

```json
{{
  "total_stages": 4,
  "estimated_total_hours": 40,
  "current_stage": 1,
  "path": [
    {{
      "stage": 1,
      "title": "哲学基础筑基",
      "chapters": ["ch01"],
      "estimated_hours": 8,
      "prerequisites": [],
      "objectives": ["掌握阴阳学说基本概念", "理解五行相生相克"],
      "learning_sequence": [
        {{
          "step": 1,
          "knowledge_point": "阴阳学说的基本概念",
          "cognitive_level": "识记→理解",
          "estimated_minutes": 45,
          "resource_types": ["lecture_doc", "mind_map"],
          "review_after_steps": 3
        }}
      ],
      "assessment": "完成阴阳五行基础自测题",
      "weak_spot_reinforcement": ["五行相克与相侮的区别"]
    }}
  ],
  "review_schedule": [
    {{"after_hours": 1, "review": "阴阳基本概念闪卡"}},
    {{"after_hours": 24, "review": "五行相生相克复盘"}}
  ]
}}
```

⚠️ 学习路径仅供教育参考，非医疗建议。
"""

    expected_output = (
        "一份完整的个性化学习路径JSON，包含："
        "1) 学习阶段划分；2) 每阶段知识点序列；"
        "3) 认知层次递进；4) 评估检测点；"
        "5) 薄弱点强化计划；6) 复习时间表。"
    )

    return Task(
        description=description,
        agent=agent,
        expected_output=expected_output,
    )
