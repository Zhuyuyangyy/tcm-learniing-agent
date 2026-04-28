# -*- coding: utf-8 -*-
"""
============================================
降级兜底处理器 (Fallback Handler)
============================================
功能：
  1. 重试全部失败后触发降级逻辑，严禁未捕获异常导致程序崩溃
  2. 返回标准化降级响应文本
  3. 记录完整 ERROR 级别日志（请求参数、错误栈、重试次数）
  4. 实现故障隔离，不影响主进程

Author: Alice 🌸
============================================
"""

from __future__ import annotations

import sys
import json
import traceback
import logging
from datetime import datetime
from typing import Any, Optional
from pathlib import Path

# 使用集中式日志系统
from app.core.logger import logger

# 兜底响应文本
FALLBACK_REPLY_TEXT = "老中医正在闭目养神，请稍后再试 🌿"


# ============================================================
# 标准化降级响应
# ============================================================

class FallbackResponse:
    """
    标准降级响应结构体

    Attributes:
        success: 是否成功（fallback 时为 False）
        content: 降级回复文本
        source: 来源标记（固定为 "fallback"）
        request_id: 请求标识（透传）
        error_info: 错误详情（可选）
        timestamp: 时间戳
    """

    def __init__(
        self,
        content: str = FALLBACK_REPLY_TEXT,
        source: str = "fallback",
        request_id: Optional[str] = None,
        error_info: Optional[dict] = None,
        extra_data: Optional[dict] = None,
    ):
        self.success = False
        self.content = content
        self.source = source
        self.request_id = request_id
        self.error_info = error_info or {}
        self.extra_data = extra_data or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "content": self.content,
            "source": self.source,
            "request_id": self.request_id,
            "error_info": self.error_info,
            "extra_data": self.extra_data,
            "timestamp": self.timestamp,
        }

    def __repr__(self):
        return f"FallbackResponse(source={self.source}, request_id={self.request_id})"


# ============================================================
# Fallback 处理器
# ============================================================

class FallbackHandler:
    """
    全局降级兜底处理器

    使用方式：
        handler = FallbackHandler()

        try:
            result = await llm.chat(messages, use_fallback=True)
        except Exception as exc:
            response = handler.handle(
                exc,
                messages=messages,
                request_id="req-001",
            )
            # response 是一个 FallbackResponse
    """

    def __init__(self):
        self._logger = logger

    def handle(
        self,
        exc: Exception,
        messages: Optional[list[dict[str, str]]] = None,
        request_id: Optional[str] = None,
        retry_count: int = 0,
        api_name: str = "unknown",
        extra_data: Optional[dict] = None,
    ) -> FallbackResponse:
        """
        处理降级逻辑

        Args:
            exc: 捕获的异常对象
            messages: 原始请求消息列表
            request_id: 请求唯一标识
            retry_count: 已执行的重试次数
            api_name: API 名称
            extra_data: 额外透传数据

        Returns:
            FallbackResponse: 标准降级响应
        """
        # ---- 构造错误详情 ----
        error_info = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
            "retry_count": retry_count,
            "api_name": api_name,
            "request_messages": messages,
            "handled_at": datetime.now().isoformat(),
        }

        # ---- 记录完整 ERROR 日志 ----
        self._logger.error(
            f"❌ Fallback triggered | "
            f"api={api_name} | "
            f"request_id={request_id or 'N/A'} | "
            f"retry_count={retry_count} | "
            f"exception={type(exc).__name__}: {exc}"
        )
        self._logger.error(
            f"   Request messages: "
            f"{json.dumps(messages, ensure_ascii=False)[:200] if messages else 'N/A'}"
        )
        self._logger.error(f"   Traceback:\n{traceback.format_exc()}")

        # ---- 返回标准化降级响应 ----
        response = FallbackResponse(
            content=FALLBACK_REPLY_TEXT,
            source="fallback",
            request_id=request_id,
            error_info=error_info,
            extra_data=extra_data,
        )

        return response

    def handle_with_result(
        self,
        exc: Exception,
        fallback_result: Any,
        messages: Optional[list[dict[str, str]]] = None,
        request_id: Optional[str] = None,
        retry_count: int = 0,
        api_name: str = "unknown",
    ) -> FallbackResponse:
        """
        处理降级逻辑（自定义降级结果）

        当需要使用特定降级内容而非默认文本时使用。
        """
        error_info = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
            "retry_count": retry_count,
            "api_name": api_name,
        }

        self._logger.error(
            f"❌ Fallback triggered (custom) | "
            f"api={api_name} | "
            f"request_id={request_id or 'N/A'} | "
            f"retry_count={retry_count} | "
            f"exception={type(exc).__name__}"
        )

        return FallbackResponse(
            content=fallback_result,
            source="fallback_custom",
            request_id=request_id,
            error_info=error_info,
        )


# ============================================================
# 全局单例
# ============================================================

_fallback_handler: Optional[FallbackHandler] = None


def get_fallback_handler() -> FallbackHandler:
    """获取 FallbackHandler 全局单例"""
    global _fallback_handler
    if _fallback_handler is None:
        _fallback_handler = FallbackHandler()
    return _fallback_handler


# ============================================================
# 便捷入口
# ============================================================

def handle_fallback(
    exc: Exception,
    messages: Optional[list[dict[str, str]]] = None,
    request_id: Optional[str] = None,
    retry_count: int = 0,
    api_name: str = "LLM",
) -> FallbackResponse:
    """
    一行调用降级处理器
    """
    return get_fallback_handler().handle(
        exc=exc,
        messages=messages,
        request_id=request_id,
        retry_count=retry_count,
        api_name=api_name,
    )
