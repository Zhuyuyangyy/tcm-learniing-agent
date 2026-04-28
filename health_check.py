# -*- coding: utf-8 -*-
"""
health_check.py - TCM AI 容灾与熔断健康检查
============================================
3 个核心测试用例：
  1. API 连通性正常场景
  2. API 超时模拟场景（3次重试→降级兜底）
  3. API 500 错误模拟场景（3次重试→降级兜底）
============================================
"""

import sys
import asyncio
import unittest.mock as mock
from pathlib import Path

project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

from app.core.logger import setup_logger, logger
setup_logger(console_level="DEBUG", file_level="DEBUG")

from app.core.llm_spark import SparkChatModel, get_token_counter
from app.core.fallback_handler import get_fallback_handler, FALLBACK_REPLY_TEXT
from langchain_core.messages import HumanMessage


# ============================================================
# 辅助
# ============================================================

def test_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ============================================================
# 用例 1：API 连通性正常场景
# ============================================================

async def test_api_normal():
    """
    直接 mock httpx.AsyncClient.post 返回成功数据，
    绕过 _call_api 内部实现细节，专注于测试 LLM 层。
    """
    test_header("用例 1: API 连通性正常场景")

    llm = SparkChatModel(
        spark_app_id="test-app-id",
        spark_api_key="test-api-key",
        spark_api_secret="test-secret",
    )

    import httpx

    mock_result = {
        "choices": [{"message": {"content": "肝属木，主疏泄，属阴脏"}}],
        "usage": {"prompt_tokens": 30, "completion_tokens": 15},
    }

    # MockResponse: 充当 httpx.Response
    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            # Must return awaitable — caller uses `await response.json()`
            async def _json():
                return mock_result
            return _json()

    # MockClient: 充当 async with httpx.AsyncClient() as client
    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            return MockResponse()

    # 在 llm_spark.py 内部 patch httpx.AsyncClient
    with mock.patch("app.core.llm_spark.httpx.AsyncClient", return_value=MockClient()):
        result = await llm._agenerate(
            messages=[HumanMessage(content="肝属什么？")]
        )

    content = result.generations[0].message.content
    source = result.llm_output.get("source", "N/A")

    print(f"  响应内容: {content}")
    print(f"  source: {source}")

    assert "肝属木" in content, f"[FAIL] 期望包含'肝属木', 实际: {content}"
    assert source != "fallback", f"[FAIL] 不应为 fallback, actual={source}"
    print("[PASS] 用例 1 通过: 连通性正常，系统正常返回 LLM 内容")

    tc = get_token_counter()
    print(f"  Token统计: request_count={tc.request_count}, total_tokens={tc.total_all_tokens}")
    assert tc.request_count >= 1, "Token计数器未累加"
    print("[PASS] Token 统计正常")


# ============================================================
# 用例 2：API 超时模拟场景
# ============================================================

async def test_api_timeout():
    test_header("用例 2: API 超时模拟场景")

    llm = SparkChatModel(
        spark_app_id="test-app-id",
        spark_api_key="test-api-key",
        spark_api_secret="test-secret",
    )

    import httpx

    class TimeoutClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            raise httpx.TimeoutException("Simulated timeout")

    with mock.patch("app.core.llm_spark.httpx.AsyncClient", return_value=TimeoutClient()):
        result = await llm._agenerate(
            messages=[HumanMessage(content="肝属什么？")]
        )

    content = result.generations[0].message.content
    source = result.llm_output.get("source", "")

    print(f"  响应内容: {content}")
    print(f"  source: {source}")

    assert FALLBACK_REPLY_TEXT in content, \
        f"[FAIL] 期望兜底文本, 实际: {content}"
    assert source == "fallback", \
        f"[FAIL] 期望 source=fallback, 实际: {source}"
    print("[PASS] 用例 2 通过: 超时场景系统未崩溃，正常返回降级兜底文本")


# ============================================================
# 用例 3：API 500 错误模拟场景
# ============================================================

async def test_api_server_error():
    test_header("用例 3: API 异常返回模拟场景 (500 Server Error)")

    llm = SparkChatModel(
        spark_app_id="test-app-id",
        spark_api_key="test-api-key",
        spark_api_secret="test-secret",
    )

    import httpx

    exc_500 = httpx.HTTPStatusError(
        "500 Server Error",
        request=None,
        response=None,
    )

    class ErrorClient:
        def __init__(self, exc):
            self._exc = exc

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            raise self._exc

    with mock.patch("app.core.llm_spark.httpx.AsyncClient", return_value=ErrorClient(exc_500)):
        result = await llm._agenerate(
            messages=[HumanMessage(content="肝属什么？")]
        )

    content = result.generations[0].message.content
    source = result.llm_output.get("source", "")

    print(f"  响应内容: {content}")
    print(f"  source: {source}")

    assert FALLBACK_REPLY_TEXT in content, \
        f"[FAIL] 期望兜底文本, 实际: {content}"
    assert source == "fallback", \
        f"[FAIL] 期望 source=fallback, 实际: {source}"
    print("[PASS] 用例 3 通过: 500 异常场景系统未崩溃，正常返回降级兜底文本")


# ============================================================
# 主入口
# ============================================================

async def main():
    print("\n" + "=" * 60)
    print("  TCM AI Health Check — 容灾与熔断验证")
    print("=" * 60)

    results = {}

    try:
        await test_api_normal()
        results["用例1_连通性正常"] = "PASS"
    except Exception as e:
        logger.exception(f"用例 1 异常: {e}")
        results["用例1_连通性正常"] = f"FAIL: {e}"

    try:
        await test_api_timeout()
        results["用例2_超时模拟"] = "PASS"
    except Exception as e:
        logger.exception(f"用例 2 异常: {e}")
        results["用例2_超时模拟"] = f"FAIL: {e}"

    try:
        await test_api_server_error()
        results["用例3_服务器异常"] = "PASS"
    except Exception as e:
        logger.exception(f"用例 3 异常: {e}")
        results["用例3_服务器异常"] = f"FAIL: {e}"

    print("\n" + "=" * 60)
    print("  健康检查汇总")
    print("=" * 60)
    for name, status in results.items():
        icon = "✅" if status == "PASS" else "❌"
        print(f"  {icon} {name}: {status}")

    all_pass = all(v == "PASS" for v in results.values())
    print("\n" + "=" * 60)
    if all_pass:
        print("  ✅ 全部测试用例通过")
    else:
        print("  ❌ 存在失败用例，请检查日志")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
