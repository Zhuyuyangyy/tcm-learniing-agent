"""
============================================
Dify 工作流 LLM 封装类
============================================
功能：
  1. 实现 LangChain BaseChatModel 接口，兼容 CrewAI Agent
  2. 将 Dify workflow 作为 LLM 使用，支持 streaming
  3. 透明替换现有的 get_crewai_llm()（讯飞星火）

接口映射：
  - Dify workflow inputs.expert_select  ← role
  - Dify workflow inputs.user_question   ← user messages
  - Dify workflow outputs.answer        → text response

使用方式：
  # env 中配置 DIFY_API_KEY、DIFY_API_URL 后，
  # 在 TcmBaseAgent.llm 属性中替换为 DifyWorkflowLLM 实例即可
  # CrewAI 会自动调用 .invoke() / .stream()

⚠️ 免责声明：所有输出仅供教育学习参考，非医疗建议。
============================================
"""

import os
import json
import time
import asyncio
from typing import Any, Dict, List, Optional, Iterator, Union, AsyncIterator

import httpx
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks import CallbackManagerForLLMRun

load_dotenv()


class DifyWorkflowLLM(BaseChatModel):
    """
    Dify Workflow LLM 封装

    将 Dify workflow API 包装为 LangChain BaseChatModel，
    使其可以直接赋给 CrewAI Agent.llm，实现接口透明替换。

    使用示例：
        >>> llm = DifyWorkflowLLM(
        ...     api_url=os.getenv("DIFY_API_URL"),
        ...     api_key=os.getenv("DIFY_API_KEY"),
        ...     workflow_id=os.getenv("DIFY_WORKFLOW_ID"),
        ...     expert_type="中医通识专家",
        ... )
        >>> response = llm.invoke([HumanMessage(content="什么是阴阳五行？")])
        >>> for chunk in llm.stream([HumanMessage(content="什么是阴阳五行？")]):
        ...     print(chunk)
    """

    # ---------- LangChain BaseChatModel 必须实现字段 ----------

    vertex_: Any = None  # LangChain 标准字段（禁用时会报错）
    model: str = "dify-workflow"  # 兼容 CrewAI llm.model 字段
    temperature: float = 0.7  # Dify 不直接支持 temperature，本字段作记录用
    max_tokens: int = 2000  # 同上

    # ---------- Dify 专有配置 ----------

    api_url: str = ""
    api_key: str = ""
    workflow_id: str = ""
    expert_type: str = "中医通识专家"  # 默认专家类型
    timeout: float = 60.0
    _client: Optional[httpx.AsyncClient] = None

    class Config:
        extra = "allow"  # 允许额外字段（如 vertex_, model）

    # ---------- 初始化 ----------

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        workflow_id: Optional[str] = None,
        expert_type: str = "中医通识专家",
        timeout: float = 60.0,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ):
        # 优先使用传入参数，其次环境变量
        self.api_url = (api_url or os.getenv("DIFY_API_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("DIFY_API_KEY", "")
        self.workflow_id = workflow_id or os.getenv("DIFY_WORKFLOW_ID", "")
        self.expert_type = expert_type
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None

        super().__init__(**kwargs)  # LangChain 规范：最后调用 super

        if self.api_url and self.api_key:
            pass  # enabled
        else:
            import warnings
            warnings.warn(
                "DifyWorkflowLLM: DIFY_API_URL / DIFY_API_KEY 未配置，"
                "Dify 调用将降级返回错误。"
            )

    # ---------- 非公开属性 ----------

    @property
    def enabled(self) -> bool:
        return bool(self.api_url and self.api_key)

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    # ---------- LangChain 标准接口 ----------

    def _call_impl(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> ChatResult:
        """
        同步调用入口（CrewAI Agent.invoke() 使用）

        注意：本方法为同步封装，内部使用 asyncio.run，
        适用于 CrewAI 等同步调用场景。
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self._acall_impl(messages, stop, run_manager)
        )

    async def _acall_impl(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> ChatResult:
        """异步调用入口"""
        # 将 BaseMessage 列表转换为单个文本
        # 取最后一条 HumanMessage 的 content 作为 user_question
        user_question = ""
        expert_select = self.expert_type  # 可从 messages[0].content 解析

        # 解析 expert_select（如果首条是 system 或带有专家标记）
        if messages:
            first = messages[0]
            content = first.content if hasattr(first, "content") else str(first)
            if hasattr(first, "type") and first.type == "system":
                # 从 system message 解析专家类型（约定格式）
                if "【专家类型】" in content:
                    import re
                    m = re.search(r"【专家类型】\s*(\S+)", content)
                    if m:
                        expert_select = m.group(1)
                user_question = self._extract_question_from_messages(messages[1:])
            else:
                user_question = self._extract_question_from_messages(messages)

        # 调用 Dify workflow
        result = await self._chat_with_workflow(expert_select, user_question)

        # 解析 answer
        answer_text = ""
        if isinstance(result, dict):
            answer_text = result.get("answer", "") or str(result.get("outputs", {}))
        elif isinstance(result, str):
            answer_text = result

        # 构建 ChatResult
        ai_msg = AIMessage(content=answer_text)
        gen = ChatGeneration(message=ai_msg, generation_info={"finish_reason": "stop"})
        return ChatResult(generations=[gen])

    def _stream_impl(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> Iterator[ChatGeneration]:
        """
        流式接口（CrewAI Agent.stream() 使用）
        返回 Iterator[ChatGeneration]（每个 chunk 一个）
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        async_gen = self._astream(messages)
        while True:
            try:
                chunk = loop.run_until_complete(async_gen.__anext__())
                yield chunk
            except StopAsyncIteration:
                break

    async def _astream(
        self,
        messages: List[BaseMessage],
    ) -> AsyncIterator[ChatGeneration]:
        """
        异步流式接口
        """
        user_question = self._extract_question_from_messages(messages)
        expert_select = self.expert_type

        async for event in self._stream_with_workflow(expert_select, user_question):
            if event.get("done"):
                break
            content = event.get("content", "")
            if content:
                yield ChatGeneration(
                    message=AIMessage(content=content),
                    generation_info={"finish_reason": "stop"},
                )

    # ---------- 内部方法 ----------

    def _extract_question_from_messages(self, messages: List[BaseMessage]) -> str:
        """从 messages 中提取最后一条用户消息"""
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                return msg.content if hasattr(msg, "content") else str(msg)
        # 兜底：取最后一条
        if messages:
            return messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])
        return ""

    async def _chat_with_workflow(
        self,
        expert_select: str,
        user_question: str,
    ) -> Dict[str, Any]:
        """Blocking 调用 Dify workflow（返回 answer 文本）"""
        if not self.enabled:
            return {"error": "Dify未启用"}

        request_id = f"dify-{id(self)}-{int(time.time() * 1000) % 100000:05d}"

        payload = {
            "inputs": {
                "expert_select": expert_select,
                "user_question": user_question,
            },
            "response_mode": "blocking",
            "user": "tcm-learning-agent",
        }

        url = f"{self.api_url}/workflows/run"

        try:
            from app.core.logger import logger
            logger.debug(f"Dify调用开始 | req={request_id} | expert={expert_select} | q={user_question[:30]}")

            response = await self.client.post(url, json=payload)
            elapsed_ms = 0  # 暂不计算

            if not response.is_success:
                logger.error(f"Dify API error {response.status_code}: {response.text[:200]}")
                return {"error": f"Dify API error: {response.status_code}"}

            result = response.json()
            outputs = result.get("data", {}).get("outputs", {})
            answer_text = outputs.get("answer", "") or str(outputs)

            logger.debug(f"Dify调用成功 | req={request_id} | answer_len={len(answer_text)}")
            return {"answer": answer_text, "outputs": outputs}

        except httpx.TimeoutException:
            from app.core.logger import logger
            logger.error(f"Dify调用超时 ({self.timeout}s)")
            return {"error": f"Dify调用超时({self.timeout}s)"}
        except Exception as e:
            from app.core.logger import logger
            logger.error(f"Dify调用异常: {e}")
            return {"error": f"Dify调用异常: {e}"}

    async def _stream_with_workflow(
        self,
        expert_select: str,
        user_question: str,
    ) -> AsyncIterator[Dict]:
        """Streaming 调用 Dify workflow"""
        if not self.enabled:
            yield {"error": "Dify未启用", "done": True}
            return

        payload = {
            "inputs": {
                "expert_select": expert_select,
                "user_question": user_question,
            },
            "response_mode": "streaming",
            "user": "tcm-learning-agent",
        }

        url = f"{self.api_url}/workflows/run"

        try:
            async with self.client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data_str = line[5:].strip()
                    if data_str == "[DONE]":
                        yield {"done": True}
                        break
                    try:
                        chunk = json.loads(data_str)
                        event = chunk.get("event", "")
                        if event == "message":
                            content = chunk.get("data", {}).get("content", "")
                            yield {"content": content, "done": False}
                    except json.JSONDecodeError:
                        continue
                yield {"done": True}
        except Exception as e:
            from app.core.logger import logger
            logger.error(f"Dify流式调用异常: {e}")
            yield {"error": str(e), "done": True}

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


# ---------- 便捷工厂函数 ----------

def get_dify_llm(
    expert_type: str = "中医通识专家",
    temperature: float = 0.7,
) -> DifyWorkflowLLM:
    """
    获取 DifyWorkflowLLM 实例（替换 get_crewai_llm 的工厂函数）

    Args:
        expert_type: 专家类型，对应 Dify workflow 的 inputs.expert_select
            - 中医通识专家 / 针灸推拿专家 / 中药方剂专家 / 中医诊断专家 / 养生保健专家
        temperature: 温度参数（Dify 不直接使用，仅作记录）
    """
    return DifyWorkflowLLM(
        api_url=os.getenv("DIFY_API_URL", ""),
        api_key=os.getenv("DIFY_API_KEY", ""),
        workflow_id=os.getenv("DIFY_WORKFLOW_ID", ""),
        expert_type=expert_type,
        temperature=temperature,
    )


def get_dify_llm_for_agent(agent_key: str, temperature: float = 0.7) -> DifyWorkflowLLM:
    """
    根据 agent_key 获取对应专家类型的 DifyLLM 实例

    Args:
        agent_key: Agent 标识
            - profile_builder    → 中医通识专家
            - tcm_retriever     → 中医通识专家
            - resource_generator → 中药方剂专家
            - critique_agent    → 中医诊断专家
            - path_planner      → 养生保健专家
        temperature: 温度参数
    """
    _AGENT_EXPERT_MAP = {
        "profile_builder": "中医通识专家",
        "tcm_retriever": "中医通识专家",
        "resource_generator": "中药方剂专家",
        "critique_agent": "中医诊断专家",
        "path_planner": "养生保健专家",
    }
    expert = _AGENT_EXPERT_MAP.get(agent_key, "中医通识专家")
    return get_dify_llm(expert_type=expert, temperature=temperature)