# -*- coding: utf-8 -*-
"""
============================================
TCM AI Learning Agent — 日志系统演示脚本
============================================
验证点：
  1. 控制台彩色日志正常输出
  2. 文件日志正确写入 logs/
  3. 业务埋点函数正常工作
  4. 异常日志堆栈正确记录

用法：
  python scripts/demo_scenarios.py
"""

import sys
from pathlib import Path

# 确保项目根目录在 path 中
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

# ============================================================
# 初始化日志系统
# ============================================================
from app.core.logger import (
    logger,
    setup_logger,
    log_agent_task_received,
    log_agent_task_completed,
    log_rag_verification,
    log_critique_reject,
    log_api_error,
    log_state_transition,
)

setup_logger(console_level="DEBUG", file_level="DEBUG")


# ============================================================
# 模拟场景
# ============================================================

def run_demo():
    """完整流程演示"""
    logger.info("=" * 58)
    logger.info("🌿 TCM AI Learning Agent — 日志系统演示开始")
    logger.info("=" * 58)

    # ---- 1. Agent 追踪 ----
    logger.info("--- 场景一：Agent 追踪 ---")
    log_agent_task_received(
        "ProfileBuilder",
        "build_profile",
        "分析用户对话内容，提取学习偏好"
    )
    log_agent_task_completed(
        "ProfileBuilder",
        "build_profile",
        '{"knowledge_level": "初级", "learning_style": "视觉型", "profile_confidence": 0.92}'
    )

    # ---- 2. RAG 图谱校验 ----
    logger.info("--- 场景二：RAG 图谱校验 ---")
    # 精确匹配
    log_rag_verification(
        entity="肝[属于]阴脏",
        match_type="exact",
        confidence=0.95,
        paths=None,
        graph_edges_checked=256,
    )
    # 路径匹配
    log_rag_verification(
        entity="肝[开窍于]目",
        match_type="path",
        confidence=0.60,
        paths=[
            {"head": "肝", "relation": "属于", "tail": "五脏"},
            {"head": "五脏", "relation": "对应", "tail": "五官"},
            {"head": "五官", "relation": "开窍于", "tail": "目"},
        ],
        graph_edges_checked=256,
    )
    # 无匹配（幻觉检测）
    log_rag_verification(
        entity="肝[属金]阳脏",
        match_type="none",
        confidence=0.0,
        paths=None,
        graph_edges_checked=256,
    )

    # ---- 3. 杏林纠错官拦截 ----
    logger.info("--- 场景三：杏林纠错官拦截 [REJECT] ---")
    log_critique_reject(
        hallucination_content="肝主疏泄，属阳脏，应以清热泻火为主",
        reject_reason="知识图谱验证失败：肝的阴阳属性为阴（五行属木），并非阳脏（金）",
        confidence=0.12,
        suggested_fix="改为：肝主疏泄，属阴脏，应以滋阴养肝为主",
    )

    # ---- 4. API 异常 ----
    logger.info("--- 场景四：API 异常 ---")
    log_api_error(
        api_name="Spark（讯飞星火）",
        error_type="RateLimitError",
        error_detail="QPS 超出限制，当前每分钟 60 次，请求被限流",
        retry_count=3,
    )
    log_api_error(
        api_name="Spark（讯飞星火）",
        error_type="AuthenticationError",
        error_detail="API Key 无效或已过期，请检查 .env 配置",
        retry_count=0,
    )

    # ---- 5. 状态转换 ----
    logger.info("--- 场景五：流程状态转换 ---")
    log_state_transition("IDLE", "BUILDING_PROFILE", "user_login")
    log_state_transition("BUILDING_PROFILE", "RETRIEVING", "profile_built")
    log_state_transition("RETRIEVING", "GENERATING", "retrieval_completed")
    log_state_transition("GENERATING", "CRITIQUING", "resource_generated")
    log_state_transition("CRITIQUING", "COMPLETED", "critique_approved")

    # ---- 6. 异常堆栈记录 ----
    logger.info("--- 场景六：异常堆栈记录 ---")
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("❌ 捕获到除零异常（此处会记录完整堆栈）")

    # ---- 完成 ----
    logger.success("🌟 所有演示场景执行完毕，请查看上方彩色日志输出")
    logger.info(f"📁 文件日志已写入: {project_root / 'logs'}")


if __name__ == "__main__":
    run_demo()
