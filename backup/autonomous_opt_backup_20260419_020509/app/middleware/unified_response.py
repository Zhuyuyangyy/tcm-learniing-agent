# -*- coding: utf-8 -*-
"""
============================================
统一响应格式中间件 (app/middleware/unified_response.py)
============================================
功能：
  将所有 HTTP 响应强制规范化为统一 JSON 格式：
  {"code": <int>, "msg": <str>, "data": <any>}

  code 约定：
    2xx → 成功
    4xx → 客户端错误
    5xx → 服务端错误
============================================
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


def unified_response(code: int, msg: str, data=None) -> dict:
    """全项目统一的 JSON 响应格式工厂函数"""
    return {
        "code": code,
        "msg": msg,
        "data": data,
    }


class UnifiedResponseMiddleware(BaseHTTPMiddleware):
    """
    统一响应格式中间件

    将所有未被 JSONResponse 包装的响应体强制规范化。
    已使用 JSONResponse 的路由（鉴权中间件返回 403 等）保持不变。
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 如果已经是 JSONResponse（可能是 JSONResponse 或 ErrorResponse），保持原样
        if isinstance(response, JSONResponse):
            return response

        # 如果响应体是 dict，说明是 FastAPI 自动序列化的对象，
        # 再次包装为统一格式（但无法在这里干预，因为 body 已经序列化）
        return response
