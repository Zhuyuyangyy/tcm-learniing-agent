"""
============================================
中医多智能体基类
============================================
功能：
  1. 统一封装 CrewAI Agent 创建逻辑
  2. 自动注入讯飞星火LLM（get_crewai_llm()）
  3. 提供 get_tools() 方法，为特定Agent分配检索工具
  4. 从 config.yaml 读取 Agent 配置

⚠️ 免责声明：所有Agent生成内容仅供教育学习参考，非医疗建议。
============================================
"""

import yaml
from typing import Any, Dict, List, Optional

from crewai import Agent
from loguru import logger

from app.core.llm_spark import get_crewai_llm

# Dify LLM 支持（可选切换）
_DIFY_AVAILABLE = False
try:
    from app.core.llm_dify import get_dify_llm_for_agent
    _DIFY_AVAILABLE = True
except ImportError:
    get_dify_llm_for_agent = None  # type: ignore


class TcmBaseAgent:
    """
    中医多智能体基类

    所有Agent继承此类，统一：
      - LLM：讯飞星火（通过get_crewai_llm注入）
      - 配置：从config.yaml读取role/goal/backstory
      - 工具：根据Agent类型自动分配retriever_tool

    使用示例：
        >>> class ProfileBuilder(TcmBaseAgent):
        ...     agent_key = "profile_builder"
        ...     temperature = 0.3  # 画像构建需要确定性
        >>>
        >>> builder = ProfileBuilder()
        >>> agent = builder.create()  # 返回 CrewAI Agent 实例
    """

    # 子类必须指定对应的config.yaml中的agent key
    agent_key: str = ""

    # 子类可覆盖温度参数
    temperature: float = 0.7

    # 是否需要检索工具
    needs_retriever: bool = False

    # 是否需要图谱查询工具
    needs_graph: bool = False

    # LLM 类型："spark"（默认，讯飞星火）或 "dify"（Dify 工作流）
    llm_type: str = "spark"

    def __init__(self, config_path: str = "config.yaml"):
        """
        Args:
            config_path: config.yaml 路径
        """
        self.config = self._load_config(config_path)
        self.agent_config = self._get_agent_config()
        self._llm = None

    def _load_config(self, config_path: str) -> dict:
        """加载config.yaml"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"config.yaml未找到: {config_path}")
            return {}

    def _get_agent_config(self) -> dict:
        """从config中获取当前Agent的配置"""
        agents_config = self.config.get("agents", {})
        if self.agent_key not in agents_config:
            logger.warning(f"Agent key '{self.agent_key}' 不在config.yaml中")
            return {}
        return agents_config[self.agent_key]

    @property
    def llm(self):
        """
        获取 LLM 实例（延迟初始化）

        支持两种模式：
        - llm_type="spark": 讯飞星火（通过 get_crewai_llm 注入）
        - llm_type="dify": Dify 工作流（通过 get_dify_llm_for_agent 注入）

        当 env 中 DIFY_API_URL / DIFY_API_KEY 配置时，
        自动切换为 Dify 模式。
        """
        if self._llm is None:
            if self.llm_type == "dify" and _DIFY_AVAILABLE and get_dify_llm_for_agent is not None:
                self._llm = get_dify_llm_for_agent(
                    agent_key=self.agent_key,
                    temperature=self.temperature,
                )
                logger.info(f"✅ Agent[{self.agent_key}] LLM初始化 | type=dify | temp={self.temperature}")
            else:
                self._llm = get_crewai_llm(temperature=self.temperature)
                logger.info(f"✅ Agent[{self.agent_key}] LLM初始化 | type=spark | temp={self.temperature}")
        return self._llm

    def get_tools(self) -> List[Any]:
        """
        获取Agent可用的工具列表

        子类可覆盖此方法，添加Agent专用工具。
        基类提供：
          - needs_retriever=True: 中医知识检索工具
          - needs_graph=True: 知识图谱查询工具

        Returns:
            CrewAI Tool 列表
        """
        tools = []

        if self.needs_retriever:
            tools.append(self._create_retriever_tool())

        if self.needs_graph:
            tools.append(self._create_graph_tool())

        return tools

    def _create_retriever_tool(self):
        """
        创建中医知识检索工具（CrewAI Tool）

        该工具允许Agent在执行任务时检索中医知识库，
        确保生成内容有据可依。
        """
        from crewai.tools import tool

        @tool("中医知识库检索工具")
        def tcm_knowledge_search(query: str) -> str:
            """
            从中医基础理论知识库中检索相关内容。

            使用场景：
              - 需要查找某个中医概念的定义和解释
              - 需要获取特定章节的教材原文
              - 需要验证某个中医知识点是否在教材中

            Args:
                query: 检索查询（如"阴阳学说的基本内容"、"藏象学说中肝的功能"）

            Returns:
                检索到的知识文本
            """
            # 延迟导入，避免循环依赖
            from app.rag.vectorstore import TcmVectorStore
            import os

            store = TcmVectorStore(
                persist_dir=os.getenv("CHROMA_PERSIST_DIR", "./data/vector_db"),
                collection_name=os.getenv("CHROMA_COLLECTION_NAME", "tcm_knowledge"),
                embedding_app_id=os.getenv("SPARK_EMBEDDING_APP_ID", ""),
                embedding_api_key=os.getenv("SPARK_EMBEDDING_API_KEY", ""),
                embedding_api_secret=os.getenv("SPARK_EMBEDDING_API_SECRET", ""),
            )

            results = store.search(query, top_k=3)
            if not results:
                return "未检索到相关内容，请换个关键词尝试。"

            output_parts = []
            for i, r in enumerate(results, 1):
                output_parts.append(
                    f"【检索结果{i}】(相似度:{r['similarity']:.2f})\n"
                    f"章节: {r['metadata'].get('chapter_path', '未知')}\n"
                    f"内容: {r['content'][:500]}\n"
                )

            return "\n---\n".join(output_parts)

        return tcm_knowledge_search

    def _create_graph_tool(self):
        """
        创建中医知识图谱查询工具（CrewAI Tool）
        """
        from crewai.tools import tool

        @tool("中医知识图谱查询工具")
        def tcm_graph_query(entity: str, query_type: str = "neighbors") -> str:
            """
            从中医知识图谱中查询实体关系。

            使用场景：
              - 查询某个中医实体的关联知识（如"肝"的相关概念）
              - 验证两个实体之间的关系（如"六味地黄丸"是否包含"熟地黄"）
              - 发现实体间的间接关联路径

            Args:
                entity: 要查询的实体名（如"肝"、"六味地黄丸"、"阴虚"）
                query_type: 查询类型 - "neighbors"(邻居) / "verify"(验证关系)

            Returns:
                图谱查询结果
            """
            from app.rag.graph_service import TcmGraphService
            import os

            service = TcmGraphService()
            graph_path = os.getenv("TCM_GRAPH_PATH", "./data/knowledge_base/知识图谱")
            service.load_from_directory(graph_path)

            if query_type == "neighbors":
                neighbors = service.get_neighbors(entity)
                if not neighbors:
                    return f"知识图谱中未找到实体'{entity}'的相关关系。"

                parts = [f"实体'{entity}'的关联关系："]
                for n in neighbors:
                    direction = "→" if n["direction"] == "out" else "←"
                    parts.append(
                        f"  {direction} [{n['relation']}] {n['entity']} (置信度:{n['confidence']:.2f})"
                    )
                return "\n".join(parts)

            return f"不支持的查询类型: {query_type}"

        return tcm_graph_query

    def create(self, **overrides) -> Agent:
        """
        创建 CrewAI Agent 实例

        从config.yaml读取role/goal/backstory，
        注入讯飞星火LLM和工具列表。

        Args:
            **overrides: 覆盖Agent属性（如role, goal, backstory）

        Returns:
            CrewAI Agent 实例
        """
        role = overrides.get("role", self.agent_config.get("role", "未命名Agent"))
        goal = overrides.get("goal", self.agent_config.get("goal", ""))
        backstory = overrides.get("backstory", self.agent_config.get("backstory", ""))

        # 所有Agent都添加免责提示
        disclaimer = "\n\n⚠️ 重要：你生成的所有中医内容仅供教育学习参考，绝非医疗建议。"
        backstory_with_disclaimer = backstory + disclaimer

        agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory_with_disclaimer,
            llm=self.llm,
            tools=self.get_tools(),
            verbose=True,
            allow_delegation=False,  # 默认不允许委托，由Coordinator统一调度
            max_iter=5,  # 防止无限循环
        )

        logger.info(
            f"🤖 Agent创建完成 | role={role} | "
            f"tools={len(self.get_tools())} | "
            f"llm=spark({self.temperature})"
        )
        return agent
