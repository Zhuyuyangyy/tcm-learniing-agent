# -*- coding: utf-8 -*-
"""
============================================
鉴权中间件 (app/middleware/auth.py)
============================================
功能：
  1. 从 Authorization: Bearer {API_Key} 提取鉴权令牌
  2. 校验 API Key 合法性，未携带有效令牌 → 403 Forbidden
  3. 鉴权通过后，携带 X-User-Id 透传到后续业务
  4. 全局访问日志记录
============================================
"""

from __future__ import annotations

import time
import hashlib
from typing import Optional, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.logger import logger


# ============================================================
# 可配置的 API Key 白名单（生产环境建议从数据库或配置中心加载）
# ============================================================

# 格式：{api_key: (user_id, user_name, quota)}
_API_KEYS: dict[str, tuple[str, str, int]] = {
    # 示例 key，实际部署时请替换为真实密钥
    "sk-test-001": ("user_001", "测试用户", 1000),
    "sk-prod-001": ("user_prod", "正式用户", 10000),
}


# ============================================================
# Token 桶限流（单 key 维度）
# ============================================================

class TokenBucket:
    """简单的令牌桶限流器"""

    def __init__(self, capacity: int, refill_rate: int):
        self.capacity = capacity
        self.refill_rate = refill_rate  # 每秒补充令牌数
        self.tokens: float = float(capacity)
        self.last_refill: float = time.time()

    def consume(self, tokens: int = 1) -> bool:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


# 全局限流字典
_RATE_LIMITER: dict[str, TokenBucket] = {}


def get_rate_limiter(user_id: str, quota: int) -> TokenBucket:
    if user_id not in _RATE_LIMITER:
        _RATE_LIMITER[user_id] = TokenBucket(capacity=quota, refill_rate=quota // 60)
    return _RATE_LIMITER[user_id]


# ============================================================
# API Key 校验
# ============================================================

def validate_api_key(api_key: str) -> Optional[Tuple[str, str, int]]:
    """
    校验 API Key 是否合法。

    Returns:
        (user_id, user_name, quota) 如果合法
        None 如果不合法
    """
    return _API_KEYS.get(api_key)


def extract_bearer_token(auth_header: Optional[str]) -> Optional[str]:
    """从 'Bearer xxx' 格式提取 token"""
    if not auth_header:
        return None
    parts = auth_header.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return None


# ============================================================
# 统一响应格式
# ============================================================

def unified_response(code: int, msg: str, data=None) -> dict:
    """全项目统一的 JSON 响应格式"""
    return {
        "code": code,
        "msg": msg,
        "data": data,
    }


# ============================================================
# 鉴权中间件
# ============================================================

class AuthMiddleware(BaseHTTPMiddleware):
    """
    FastAPI 鉴权中间件

    行为：
      1. 提取 Authorization Bearer {API_Key}
      2. 校验 key 合法性，无效 → 403 + 统一响应体
      3. 通过后，在 request.state 注入 user_id / user_name
      4. 记录访问日志
      5. 限流检查
    """

    # 不需要鉴权的路径（白名单）
    EXEMPT_PATHS: set[str] = {
        "/",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/health",
        "/api/health",
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # 白名单路径直接放行
        if path in self.EXEMPT_PATHS or path.startswith("/docs"):
            return await call_next(request)

        auth_header = request.headers.get("authorization")
        token = extract_bearer_token(auth_header)

        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        full_path = str(request.url)

        if token:
            user_info = validate_api_key(token)
            if user_info:
                user_id, user_name, quota = user_info
                request.state.user_id = user_id
                request.state.user_name = user_name
                request.state.api_key = token

                # 限流检查
                limiter = get_rate_limiter(user_id, quota)
                if not limiter.consume():
                    logger.warning(
                        f"⏳ 限流触发 | user={user_id} | ip={client_ip} | "
                        f"path={full_path} | 配额耗尽"
                    )
                    return JSONResponse(
                        status_code=429,
                        content=unified_response(
                            429, "请求频率超限，请稍后重试", None
                        ),
                    )

                logger.info(
                    f"🔓 鉴权通过 | user={user_id}({user_name}) | "
                    f"ip={client_ip} | {method} {full_path}"
                )
            else:
                logger.warning(
                    f"🔒 鉴权失败 | ip={client_ip} | "
                    f"method={method} | path={full_path} | 无效key"
                )
                return JSONResponse(
                    status_code=403,
                    content=unified_response(
                        403, "API Key无效或已过期", None
                    ),
                )
        else:
            logger.warning(
                f"🔒 鉴权失败 | ip={client_ip} | "
                f"method={method} | path={full_path} | 缺失token"
            )
            return JSONResponse(
                status_code=403,
                content=unified_response(
                    403, "缺少Authorization Bearer令牌", None
                ),
            )

        response = await call_next(request)
        return response
