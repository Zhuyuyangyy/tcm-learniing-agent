# -*- coding: utf-8 -*-
"""
============================================
讯飞星火大模型 LLM 封装模块 (核心文件)
============================================
功能：
  1. 重试装饰器：Tenacity 指数退避（3次重试: 1s→2s→4s，最大间隔10s）
  2. 降级兜底：重试全败 → FallbackHandler，返回预设兜底文本
  3. Token 统计：每次调用记录输入/输出/累计消耗（INFO 级别）
  4. 兼容 LangChain BaseChatModel & CrewAI

⚠️ 免责声明：所有AI生成内容仅供教育学习参考，非医疗建议。
============================================
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
import logging
from typing import Any, Dict, List, Optional, Iterator

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult

# 使用集中式日志系统
from app.core.logger import logger, log_api_error
from app.core.fallback_handler import get_fallback_handler, FALLBACK_REPLY_TEXT


# ============================================================
# 可重试的异常类型
# ============================================================

RETRYABLE_EXCEPTIONS = (
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.NetworkError,
    httpx.RemoteProtocolError,
    httpx.HTTPStatusError,      # 5xx errors checked in retry logic
    ConnectionResetError,
    ConnectionError,
    TimeoutError,
)


# ============================================================
# 全局 Token 计数器
# ============================================================

class TokenCounter:
    """全局 Token 消耗计数器"""

    def __init__(self):
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_all_tokens: int = 0
        self.request_count: int = 0
        self._lock = asyncio.Lock()

    def add(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        request_id: str,
    ) -> dict:
        """累加 token 消耗，返回统计快照"""
        total = prompt_tokens + completion_tokens
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_all_tokens += total
        self.request_count += 1

        stats = {
            "request_id": request_id,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total,
            "global_prompt_tokens": self.total_prompt_tokens,
            "global_completion_tokens": self.total_completion_tokens,
            "global_total_tokens": self.total_all_tokens,
            "request_count": self.request_count,
        }

        # INFO 级别记录本次消耗
        logger.info(
            f"💰 Token消耗 | "
            f"req={request_id} | "
            f"prompt={prompt_tokens} | "
            f"completion={completion_tokens} | "
            f"total={total} | "
            f"[全局] prompt={self.total_prompt_tokens} "
            f"completion={self.total_completion_tokens} "
            f"total={self.total_all_tokens}"
        )

        return stats


# 全局单例
_token_counter = TokenCounter()


def get_token_counter() -> TokenCounter:
    return _token_counter


# ============================================================
# 重试前 sleep 日志（每次重试记录 WARNING）
# ============================================================

def _before_sleep_retry(retry_state):
    """每次重试触发时的 WARNING 日志"""
    attempt = retry_state.attempt_number
    exc = retry_state.outcome.exception()
    wait = retry_state.next_action.sleep if retry_state.next_action else 0

    logger.warning(
        f"🔄 LLM重试 | "
        f"attempt={attempt}/3 | "
        f"reason={type(exc).__name__}: {exc} | "
        f"wait={wait:.1f}s before next retry"
    )


# ============================================================
# 讯飞星火 ChatModel（兼容 LangChain & CrewAI）
# ============================================================

class SparkChatModel(BaseChatModel):
    """
    讯飞星火大模型 LangChain 封装（带容灾）

    特性：
      1. Tenacity 指数退避重试（最多 3 次，间隔 1s→2s→4s，上限 10s）
      2. 重试全败 → 自动降级兜底，不抛未捕获异常
      3. 每次成功调用记录 Token 消耗（INFO 级别）
      4. 兼容 LangChain BaseChatModel + CrewAI Agent llm 参数
    """

    # ---- Pydantic 字段定义 ----
    spark_app_id: str = ""
    spark_api_key: str = ""
    spark_api_secret: str = ""
    spark_model_version: str = "generalv3.5"
    temperature: float = 0.7
    max_tokens: int = 4096
    top_k: int = 4

    spark_http_url: str = (
        "https://spark-api-open.xf-yun.com/v1/chat/completions"
    )

    class Config:
        arbitrary_types_allowed = True

    @property
    def _llm_type(self) -> str:
        return "spark-chat-model"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.spark_model_version,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

    # ============================================================
    # 核心：HTTP API 调用（带重试 + 兜底）
    # ============================================================

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        同步生成（LangChain 必须实现）
        内部自动处理：重试 → 全败降级兜底
        """
        request_id = f"sync-{uuid.uuid4().hex[:8]}"
        spark_messages = _messages_to_spark_format(messages)

        auth_token = f"Bearer {self.spark_api_key}:{self.spark_api_secret}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_token,
        }

        request_body = {
            "model": kwargs.get("model", self.spark_model_version),
            "messages": spark_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "top_k": kwargs.get("top_k", self.top_k),
        }

        attempt = 0
        last_exc: Optional[Exception] = None

        while attempt < 3:
            attempt += 1
            try:
                with httpx.Client(timeout=60.0) as client:
                    response = client.post(
                        self.spark_http_url,
                        json=request_body,
                        headers=headers,
                    )

                    # 5xx 服务器错误 → 可重试
                    if response.status_code >= 500:
                        raise httpx.HTTPStatusError(
                            f"Server error: {response.status_code}",
                            request=response.request,
                            response=response,
                        )

                    response.raise_for_status()
                    result_data = response.json()
                    break

            except RETRYABLE_EXCEPTIONS as exc:
                last_exc = exc
                if attempt < 3:
                    wait = min(1 * (2 ** (attempt - 1)), 10)
                    logger.warning(
                        f"🔄 LLM重试 | req={request_id} | "
                        f"attempt={attempt}/3 | "
                        f"reason={type(exc).__name__}: {exc} | "
                        f"wait={wait:.1f}s"
                    )
                    import time as t
                    t.sleep(wait)
                else:
                    break

        else:
            # ---- 全败：触发降级兜底 ----
            logger.error(
                f"❌ LLM全败 | req={request_id} | "
                f"all 3 attempts failed, returning fallback"
            )
            fallback = get_fallback_handler().handle(
                exc=last_exc,
                messages=spark_messages,
                request_id=request_id,
                retry_count=attempt,
                api_name="Spark",
            )
            ai_message = AIMessage(content=fallback.content)
            return ChatResult(
                generations=[ChatGeneration(message=ai_message)],
                llm_output={
                    "model": self.spark_model_version,
                    "usage": {},
                    "source": fallback.source,
                },
            )

        # ---- 解析成功响应 + 记录 Token ----
        try:
            content = result_data["choices"][0]["message"]["content"]
            usage = result_data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)

            # Token 统计
            get_token_counter().add(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                request_id=request_id,
            )

        except (KeyError, IndexError) as exc:
            log_api_error("Spark", "ResponseParseError", str(exc))
            ai_message = AIMessage(content="内容生成异常，请稍后重试")
            return ChatResult(generations=[ChatGeneration(message=ai_message)])

        ai_message = AIMessage(content=content)
        return ChatResult(
            generations=[ChatGeneration(message=ai_message)],
            llm_output={
                "model": self.spark_model_version,
                "usage": usage,
            },
        )

    # ============================================================
    # 异步生成
    # ============================================================

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        异步生成（带 Tenacity 重试 + 降级兜底）
        """
        request_id = f"async-{uuid.uuid4().hex[:8]}"
        spark_messages = _messages_to_spark_format(messages)

        auth_token = f"Bearer {self.spark_api_key}:{self.spark_api_secret}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_token,
        }

        request_body = {
            "model": kwargs.get("model", self.spark_model_version),
            "messages": spark_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
            before_sleep=_before_sleep_retry,
            reraise=True,
        )
        async def _call_api():
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.spark_http_url,
                    json=request_body,
                    headers=headers,
                )
                if response.status_code >= 500:
                    raise httpx.HTTPStatusError(
                        f"Server error: {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                response.raise_for_status()
                return await response.json()

        try:
            result_data = await _call_api()
        except RETRYABLE_EXCEPTIONS as exc:
            logger.error(
                f"❌ LLM全败(异步) | req={request_id} | "
                f"all 3 attempts failed"
            )
            fallback = get_fallback_handler().handle(
                exc=exc,
                messages=spark_messages,
                request_id=request_id,
                retry_count=3,
                api_name="Spark",
            )
            ai_message = AIMessage(content=fallback.content)
            return ChatResult(
                generations=[ChatGeneration(message=ai_message)],
                llm_output={"model": self.spark_model_version, "usage": {}, "source": fallback.source},
            )

        # 解析成功响应 + Token 统计
        try:
            content = result_data["choices"][0]["message"]["content"]
            usage = result_data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)

            get_token_counter().add(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                request_id=request_id,
            )

        except (KeyError, IndexError) as exc:
            log_api_error("Spark", "ResponseParseError", str(exc))
            ai_message = AIMessage(content="内容生成异常，请稍后重试")
            return ChatResult(generations=[ChatGeneration(message=ai_message)])

        ai_message = AIMessage(content=content)
        return ChatResult(
            generations=[ChatGeneration(message=ai_message)],
            llm_output={"model": self.spark_model_version, "usage": usage},
        )

    # ============================================================
    # 流式输出
    # ============================================================

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGeneration]:
        """流式生成（SSE）"""
        request_id = f"stream-{uuid.uuid4().hex[:8]}"
        spark_messages = _messages_to_spark_format(messages)

        auth_token = f"Bearer {self.spark_api_key}:{self.spark_api_secret}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_token,
            "Accept": "text/event-stream",
        }

        request_body = {
            "model": kwargs.get("model", self.spark_model_version),
            "messages": spark_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "stream": True,
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                with client.stream(
                    "POST",
                    self.spark_http_url,
                    json=request_body,
                    headers=headers,
                ) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield ChatGeneration(
                                    message=AIMessage(content=content)
                                )
                        except (json.JSONDecodeError, KeyError):
                            continue
        except RETRYABLE_EXCEPTIONS as exc:
            logger.error(
                f"❌ LLM流式全败 | req={request_id} | "
                f"returning fallback"
            )
            fallback = get_fallback_handler().handle(
                exc=exc,
                messages=spark_messages,
                request_id=request_id,
                retry_count=3,
                api_name="Spark",
            )
            yield ChatGeneration(message=AIMessage(content=fallback.content))


# ============================================================
# 消息格式转换
# ============================================================

def _messages_to_spark_format(messages: List[BaseMessage]) -> List[Dict[str, str]]:
    """LangChain Message → 讯飞星火 API 格式"""
    spark_messages = []
    for msg in messages:
        if isinstance(msg, SystemMessage):
            spark_messages.append({"role": "system", "content": msg.content})
        elif isinstance(msg, HumanMessage):
            spark_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            spark_messages.append({"role": "assistant", "content": msg.content})
        else:
            role_map = {"system": "system", "human": "user", "ai": "assistant"}
            role = role_map.get(msg.type, "user")
            spark_messages.append({"role": role, "content": str(msg.content)})
    return spark_messages


# ============================================================
# 工厂函数
# ============================================================

def create_spark_llm(
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> SparkChatModel:
    """从环境变量创建星火 LLM 实例"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    return SparkChatModel(
        spark_app_id=os.getenv("SPARK_APP_ID", ""),
        spark_api_key=os.getenv("SPARK_API_KEY", ""),
        spark_api_secret=os.getenv("SPARK_API_SECRET", ""),
        spark_model_version=os.getenv("SPARK_API_VERSION", "generalv3.5"),
        temperature=temperature or float(os.getenv("SPARK_TEMPERATURE", "0.7")),
        max_tokens=max_tokens or int(os.getenv("SPARK_MAX_TOKENS", "4096")),
    )


def get_crewai_llm(temperature: float = 0.7) -> SparkChatModel:
    """获取 CrewAI 兼容 LLM 实例"""
    llm = create_spark_llm(temperature=temperature)
    logger.info(
        f"✅ CrewAI LLM 初始化完成 | "
        f"model={llm.spark_model_version} | temp={temperature}"
    )
    return llm
