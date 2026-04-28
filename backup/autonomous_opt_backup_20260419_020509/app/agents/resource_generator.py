"""
============================================
Agent3: 个性化资源生成专家 (ResourceGeneratorAgent)
============================================
功能：
  根据学习画像和检索到的知识，生成5种以上的个性化多模态学习资源。

资源类型（Factory模式）：
  1. lecture_doc      — 讲解文档（Markdown）
  2. mind_map         — 思维导图（JSON，前端渲染）
  3. quiz_bank        — 练习题库（JSON）
  4. extended_reading — 拓展阅读（Markdown）
  5. animation_desc   — 教学动画描述（JSON，含3D坐标/经络数据）
  6. practice_case    — 实操案例（Markdown）

关键：animation_desc 必须包含适配前端3D渲染的结构化JSON，
  如穴位3D坐标、经络连线数据，供WebGL/Three.js直接消费。

⚠️ 免责声明：所有生成内容仅供教育学习参考，非医疗建议。
============================================
"""

from typing import Any, Callable, Dict, List, Optional

from crewai import Agent, Task
from loguru import logger

from app.agents.base_agent import TcmBaseAgent


# ============================================================
# 资源生成 Factory 模式
# ============================================================

class ResourceFactory:
    """
    资源生成工厂

    根据 resource_type 调用对应的生成 Prompt 模板，
    确保每种资源类型的输出格式统一、结构清晰。

    使用示例：
        >>> factory = ResourceFactory()
        >>> prompt = factory.get_prompt("animation_desc", knowledge_point="手太阴肺经")
    """

    # 各资源类型的Prompt模板
    _TEMPLATES = {
        "lecture_doc": """
请生成一份《{knowledge_point}》的讲解文档。

要求：
- 适配学习者认知层次：{cognitive_level}
- 包含：定义 → 分类 → 核心要点 → 临床意义 → 学习小结
- 每个概念必须标注教材出处章节
- 末尾附加3-5个思考题引导深入理解

输出格式：Markdown
""",

        "mind_map": """
请生成《{knowledge_point}》的思维导图结构数据。

要求：
- 以"{knowledge_point}"为中心节点
- 展开{depth}层关联概念
- 每个节点包含：id、label、children、description
- 节点之间的关联关系必须基于教材逻辑

输出格式：严格JSON，结构如下：
```json
{{
  "id": "root",
  "label": "{knowledge_point}",
  "description": "中心概念简述",
  "children": [
    {{
      "id": "n1",
      "label": "子概念1",
      "description": "...",
      "children": []
    }}
  ]
}}
```
""",

        "quiz_bank": """
请围绕《{knowledge_point}》生成练习题库。

要求：
- 生成{count}道题目
- 难度级别：{difficulty}
- 题型分布：单选题{single_count}道 + 多选题{multi_count}道 + 判断题{judge_count}道
- 每道题必须标注考查的知识点
- 解析必须引用教材原文

输出格式：严格JSON，结构如下：
```json
{{
  "topic": "{knowledge_point}",
  "difficulty": "{difficulty}",
  "questions": [
    {{
      "id": 1,
      "type": "single",
      "question": "题目内容",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "answer": "B",
      "explanation": "解析（含教材引用）",
      "knowledge_point": "考查知识点"
    }}
  ]
}}
```
""",

        "extended_reading": """
请推荐《{knowledge_point}》相关的拓展阅读材料。

要求：
- 推荐类型：{reading_type}（经典原文/现代研究/临床案例）
- 每条推荐包含：标题、来源、摘要、推荐理由
- 优先推荐与学习者画像（{cognitive_level}）匹配的内容

输出格式：Markdown，每条推荐用二级标题
""",

        "animation_desc": """
请生成《{knowledge_point}》的教学动画描述脚本。

⚠️ 这是3D可视化核心！输出的JSON将被前端Three.js组件直接消费。

要求：
- 描述一个完整的3D动画场景
- 必须包含以下结构化数据：

1. **场景设置**：camera位置、灯光、背景
2. **3D模型数据**：
   - 如果是经络：包含穴位3D坐标(基于人体标准模型)、经络连线数据
   - 如果是藏象：包含脏腑3D位置、颜色、标注
   - 如果是阴阳五行：包含五色对应、方位映射
3. **动画时间轴**：关键帧列表，每个关键帧标注标注文字、相机运动
4. **交互节点**：用户可点击的3D热点，触发弹出解释

输出格式：严格JSON，结构如下：
```json
{{
  "animation_id": "anim_{knowledge_point}",
  "title": "{knowledge_point} 3D教学动画",
  "scene": {{
    "camera": {{ "position": [0, 1.6, 2], "target": [0, 1, 0] }},
    "lights": [
      {{ "type": "ambient", "color": "#ffffff", "intensity": 0.6 }},
      {{ "type": "directional", "color": "#ffffff", "intensity": 0.8, "position": [5, 8, 5] }}
    ],
    "background": "#1a1a2e"
  }},
  "models": [
    {{
      "id": "body_model",
      "type": "human_body",
      "position": [0, 0, 0],
      "opacity": 0.3
    }}
  ],
  "point_coordinates": [
    {{
      "id": "acup_zhongfu",
      "name": "中府",
      "description": "肺经募穴，位于胸前壁外上方",
      "position_3d": {{ "x": 0.15, "y": 1.45, "z": 0.05 }},
      "category": "穴位",
      "meridian": "手太阴肺经",
      "color": "#ff6b6b",
      "radius": 0.02
    }},
    {{
      "id": "acup_yunmen",
      "name": "云门",
      "description": "肺经穴位，位于锁骨下窝凹陷处",
      "position_3d": {{ "x": 0.18, "y": 1.48, "z": 0.03 }},
      "category": "穴位",
      "meridian": "手太阴肺经",
      "color": "#ff6b6b",
      "radius": 0.02
    }}
  ],
  "path_lines": [
    {{
      "id": "meridian_lung",
      "name": "手太阴肺经",
      "type": "meridian_line",
      "color": "#00ff88",
      "width": 2.0,
      "point_ids": ["acup_zhongfu", "acup_yunmen"],
      "path_points_3d": [
        {{ "x": 0.15, "y": 1.45, "z": 0.05 }},
        {{ "x": 0.18, "y": 1.48, "z": 0.03 }}
      ],
      "animation": {{ "type": "flow", "speed": 0.5, "direction": "proximal" }}
    }}
  ],
  "camera_focus": {{
    "default": {{ "position": [0, 1.6, 2], "target": [0, 1, 0], "fov": 45 }},
    "closeup": {{ "position": [0, 1.5, 0.8], "target": [0, 1.4, 0], "fov": 30 }},
    "overview": {{ "position": [0, 2.5, 3], "target": [0, 1, 0], "fov": 50 }}
  }},
  "timeline": [
    {{
      "time": 0,
      "action": "show_model",
      "target": "body_model",
      "label": "人体模型加载",
      "narration": "现在让我们来了解{knowledge_point}的分布走向",
      "camera_focus": "overview"
    }},
    {{
      "time": 3,
      "action": "highlight_path",
      "target": "meridian_lung",
      "label": "肺经循行",
      "narration": "手太阴肺经起于中府，沿手臂内侧前行...",
      "camera_focus": "closeup"
    }}
  ],
  "hotspots": [
    {{
      "id": "hs_1",
      "point_id": "acup_zhongfu",
      "position_3d": {{ "x": 0.15, "y": 1.45, "z": 0.05 }},
      "label": "中府穴",
      "popup_title": "中府",
      "popup_content": "肺经募穴，位于胸前壁外上方...",
      "color": "#ff6b6b"
    }}
  ]
}}
```

⚠️ 关键字段说明（前端Three.js必须读取）：
- **point_coordinates**: 所有穴位的3D坐标列表，每个点含position_3d(x,y,z)，前端据此渲染球体标记
- **path_lines**: 经络/血管等连线数据，含path_points_3d坐标序列，前端据此绘制3D管线
- **camera_focus**: 建议视角预设(default/closeup/overview)，前端据此设置Three.js相机
- 坐标系：基于标准人体模型（单位：米，原点在脚底中心，Y轴向上）
""",

        "practice_case": """
请基于{syndrome_type}设计一个中医辨证论治的教学案例。

要求：
- 案例必须包含：主诉 → 四诊信息 → 辨证分析 → 治则治法 → 方药
- 辨证过程必须体现清晰的逻辑链条
- 每一步都要标注与教材的对应关系
- 必须在案例开头和结尾添加免责声明

输出格式：Markdown，结构化呈现
⚠️ 此案例仅供教学演示，非真实临床诊疗建议。
""",
    }

    @classmethod
    def get_prompt(
        cls,
        resource_type: str,
        **kwargs,
    ) -> str:
        """
        获取资源生成的Prompt

        Args:
            resource_type: 资源类型ID
            **kwargs: 模板变量（如knowledge_point, cognitive_level等）

        Returns:
            格式化后的Prompt字符串
        """
        template = cls._TEMPLATES.get(resource_type)
        if not template:
            raise ValueError(f"不支持的资源类型: {resource_type}")

        # 填充模板变量，未提供的用默认值
        default_kwargs = {
            "knowledge_point": "未知知识点",
            "cognitive_level": "理解",
            "depth": 3,
            "count": 10,
            "difficulty": "中等",
            "single_count": 4,
            "multi_count": 3,
            "judge_count": 3,
            "reading_type": "经典原文",
            "syndrome_type": "常见证型",
        }
        default_kwargs.update(kwargs)

        return template.format(**default_kwargs)

    @classmethod
    def get_supported_types(cls) -> List[str]:
        """获取支持的资源类型列表"""
        return list(cls._TEMPLATES.keys())


# ============================================================
# ResourceGeneratorAgent
# ============================================================

class ResourceGeneratorAgent(TcmBaseAgent):
    """
    个性化资源生成专家

    根据画像和检索结果，使用Factory模式生成5+种多模态资源。
    温度0.8，资源生成需要创意和多样性。
    """

    agent_key = "resource_generator"
    temperature = 0.8  # 资源生成需要创意
    needs_retriever = True  # 必须检索，确保有据可依
    needs_graph = False

    def create(self, **overrides) -> Agent:
        """创建资源生成专家Agent"""
        custom_backstory = overrides.pop("backstory", None) or """
你是一位创新教育设计专家，精通多模态教学资源开发。

你的核心原则：
1. **有据可依**：每种资源都必须基于RAG检索结果生成，绝不凭空编造
2. **因材施教**：根据学习者的知识水平和认知能力调整内容深度
3. **多模态适配**：不同学习风格用不同资源类型（视觉型→思维导图，实践型→案例）
4. **3D可视化**：经络、藏象等内容必须生成适配Three.js的3D动画数据

你的资源生成流程：
  a) 先确认学习者的关键需求（来自画像）
  b) 从检索结果中提取核心知识素材
  c) 选择最适合的资源类型组合
  d) 使用ResourceFactory模板生成结构化输出
  e) 每种资源末尾附加免责声明

⚠️ 你生成的所有中医内容仅供教育学习参考，绝非医疗建议。
"""
        return super().create(backstory=custom_backstory, **overrides)


def create_resource_generation_task(
    agent: Agent,
    profile_data: Dict[str, Any],
    retrieval_results: str,
    resource_types: Optional[List[str]] = None,
    knowledge_point: str = "",
) -> Task:
    """
    创建资源生成任务

    Args:
        agent: ResourceGeneratorAgent实例
        profile_data: 学习者画像数据
        retrieval_results: RAG检索结果文本
        resource_types: 要生成的资源类型列表（默认全类型）
        knowledge_point: 核心知识点

    Returns:
        CrewAI Task 实例
    """
    import json

    if not resource_types:
        resource_types = ResourceFactory.get_supported_types()

    # 根据画像自动推荐资源类型
    profile_text = json.dumps(profile_data, ensure_ascii=False, indent=2)
    type_list = ", ".join(resource_types)

    # 为每种资源类型生成对应的Prompt片段
    resource_prompts = []
    for rt in resource_types:
        prompt = ResourceFactory.get_prompt(
            rt,
            knowledge_point=knowledge_point or "中医基础理论",
            cognitive_level=profile_data.get("cognitive_ability", {}).get("value", "理解"),
        )
        resource_prompts.append(f"### 资源类型：{rt}\n{prompt}")

    all_resource_prompts = "\n\n---\n\n".join(resource_prompts)

    description = f"""
## 任务：生成个性化多模态学习资源

### 学习者画像：
{profile_text}

### 知识检索结果（必须基于此生成，不可编造）：
{retrieval_results}

### 核心知识点：{knowledge_point or "根据画像和检索结果确定"}

### 需要生成的资源类型：{type_list}

{all_resource_prompts}

## 通用要求：
1. 每种资源都必须基于上面的检索结果，不可脱离教材编造
2. 根据学习者画像调整深度和表达方式
3. 所有JSON格式必须严格可解析（不要有多余的注释或格式错误）
4. 每种资源末尾附加：⚠️ 仅供教育学习参考，非医疗建议

## 输出格式：
将所有资源按类型打包为一个JSON：
```json
{{
  "knowledge_point": "...",
  "profile_summary": "...",
  "resources": {{
    "lecture_doc": {{ "type": "markdown", "content": "..." }},
    "mind_map": {{ "type": "json", "content": {{...}} }},
    "quiz_bank": {{ "type": "json", "content": {{...}} }},
    "extended_reading": {{ "type": "markdown", "content": "..." }},
    "animation_desc": {{ "type": "json", "content": {{...}} }},
    "practice_case": {{ "type": "markdown", "content": "..." }}
  }},
  "disclaimer": "⚠️ 所有内容由AI生成，基于中医教材知识库检索，仅供教育学习参考，非医疗建议。"
}}
```
"""

    expected_output = (
        "一份包含5+种资源类型的JSON包，每种资源结构化输出，"
        "animation_desc包含3D坐标数据可供Three.js渲染。"
        "所有内容基于检索结果，无幻觉编造。"
    )

    return Task(
        description=description,
        agent=agent,
        expected_output=expected_output,
    )
