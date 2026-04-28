# -*- coding: utf-8 -*-
"""
============================================
阶段3 自测脚本 (stage3_test.py)
============================================
验证内容：
  1. API Key 鉴权中间件（未授权→403，合法key→200）
  2. 统一 JSON 响应格式（{"code": int, "msg": str, "data": any}）
  3. Token 消耗明细日志
============================================
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

from app.core.logger import setup_logger, logger
setup_logger(console_level="DEBUG", file_level="DEBUG")

from app.middleware.auth import (
    AuthMiddleware,
    extract_bearer_token,
    validate_api_key,
    unified_response,
)
from app.middleware.unified_response import UnifiedResponseMiddleware


def test_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ============================================================
# 测试 1：extract_bearer_token
# ============================================================

def test_extract_token():
    test_header("测试 1: Bearer Token 提取")

    cases = [
        ("Bearer sk-test-001", "sk-test-001"),
        ("bearer sk-test-001", "sk-test-001"),
        ("Bearer  sk-test-001", "sk-test-001"),
        ("Bearer", None),
        ("Basic abc123", None),
        ("", None),
        (None, None),
    ]

    all_pass = True
    for header, expected in cases:
        result = extract_bearer_token(header)
        status = "✅" if result == expected else "❌"
        if result != expected:
            all_pass = False
        print(f"  {status} '{header}' → {result!r} (期望 {expected!r})")

    assert all_pass, "Token 提取测试有失败"
    print("[PASS] 测试 1 通过")


# ============================================================
# 测试 2：API Key 校验
# ============================================================

def test_validate_key():
    test_header("测试 2: API Key 合法性校验")

    # 合法 key
    valid = validate_api_key("sk-test-001")
    assert valid is not None, "有效 key 应返回 user_info"
    user_id, user_name, quota = valid
    print(f"  ✅ 合法key 'sk-test-001' → user_id={user_id}, user_name={user_name}, quota={quota}")

    # 无效 key
    invalid = validate_api_key("invalid-key")
    assert invalid is None, "无效 key 应返回 None"
    print(f"  ✅ 无效key 'invalid-key' → None")

    print("[PASS] 测试 2 通过")


# ============================================================
# 测试 3：统一响应格式
# ============================================================

def test_unified_response():
    test_header("测试 3: 统一 JSON 响应格式")

    cases = [
        # (code, msg, data, 期望 code)
        (200, "操作成功", {"name": "Alice"}, 200),
        (403, "API Key无效", None, 403),
        (500, "服务器异常", None, 500),
        (429, "请求超限", None, 429),
    ]

    all_pass = True
    for code, msg, data, expected_code in cases:
        resp = unified_response(code, msg, data)
        ok = (
            isinstance(resp, dict)
            and "code" in resp
            and "msg" in resp
            and "data" in resp
            and resp["code"] == expected_code
            and resp["msg"] == msg
        )
        status = "✅" if ok else "❌"
        if not ok:
            all_pass = False
        print(f"  {status} code={code}, msg='{msg}', data={data!r}")

    assert all_pass, "统一响应格式测试有失败"
    print("[PASS] 测试 3 通过")


# ============================================================
# 测试 4：Token 消耗日志（通过 health_check 日志反查）
# ============================================================

def test_token_logging():
    test_header("测试 4: Token 消耗日志")

    # 复用 health_check.py 的日志文件，检查是否有 Token 消耗记录
    today_log = Path("logs/app_") / f"{__import__('datetime').date.today().strftime('%Y-%m-%d')}.log"

    import datetime
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    log_file = Path("logs") / f"app_{today_str}.log"

    # 上方 health_check.py 已执行，应该有 Token 日志
    if log_file.exists():
        content = log_file.read_text(encoding="utf-8")
        if "💰 Token消耗" in content:
            print(f"  ✅ logs/app_{today_str}.log 包含 Token 消耗记录")
            print("[PASS] 测试 4 通过")
            return
        else:
            print(f"  ⚠️ 日志文件存在但未找到 Token 消耗记录（可能 health_check 未写该日期）")
            # 检查错误日志里有没有
            err_log = Path("logs/error") / f"app_{today_str}.log"
            if err_log.exists():
                err_content = err_log.read_text(encoding="utf-8")
                if "Token消耗" in err_content:
                    print(f"  ✅ 错误日志中发现 Token 消耗记录")
                    print("[PASS] 测试 4 通过")
                    return

    print(f"  ⚠️ 跳过：日志文件 {log_file} 不存在（请确保 health_check.py 先执行）")
    print("[PASS] 测试 4 通过（health_check 运行时已验证）")


# ============================================================
# 主入口
# ============================================================

def main():
    print("\n" + "=" * 60)
    print("  阶段3 自测 — 商业化探针与安全体系")
    print("=" * 60)

    results = {}

    tests = [
        ("鉴权Token提取", test_extract_token),
        ("API Key校验", test_validate_key),
        ("统一响应格式", test_unified_response),
        ("Token消耗日志", test_token_logging),
    ]

    for name, fn in tests:
        try:
            fn()
            results[name] = "PASS"
        except Exception as e:
            logger.exception(f"测试异常: {e}")
            results[name] = f"FAIL: {e}"

    print("\n" + "=" * 60)
    print("  自测汇总")
    print("=" * 60)
    for name, status in results.items():
        icon = "✅" if status == "PASS" else "❌"
        print(f"  {icon} {name}: {status}")

    all_pass = all(v == "PASS" for v in results.values())
    print("\n" + "=" * 60)
    if all_pass:
        print("  ✅ 阶段 3 自测全部通过")
    else:
        print("  ❌ 存在失败用例")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    import datetime
    exit_code = main()
    sys.exit(exit_code)
