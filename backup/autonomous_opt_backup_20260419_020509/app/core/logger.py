# -*- coding: utf-8 -*-
"""
============================================
集中式日志配置 (Loguru) — 升级版
============================================
功能：
  1. 控制台彩色输出，严格区分 DEBUG/INFO/WARNING/ERROR/CRITICAL 5 个级别
  2. 文件日志按天滚动归档，保留 30 天
  3. ERROR 及以上级别单独归档至 logs/error/ 目录
  4. 自动创建 logs/ 目录
  5. 导出全局单例 logger 实例，供全项目直接导入使用

日志级别与配色：
  DEBUG   🔵  — 详细诊断信息（仅文件日志）
  INFO     🟢  — 常规业务输出、流程节点
  WARNING  🟡  — 警告提示、纠错拦截
  ERROR    🔴  — API 异常、调用失败
  CRITICAL 💥  — 严重故障、进程终止

日志文件：
  logs/app_YYYY-MM-DD.log          — 全量日志（按天滚动，保留 30 天）
  logs/error/app_YYYY-MM-DD.log    — ERROR+ 单独归档

使用方式：
  from app.core.logger import logger
  logger.info("Agent 接收任务: {}", task_name)

业务埋点函数（直接调用）：
  from app.core.logger import (
      log_agent_task_received,
      log_agent_task_completed,
      log_rag_verification,
      log_critique_reject,
      log_api_error,
      log_state_transition,
  )

Author: Alice 🌸
============================================
"""

import os
import sys
import logging
from pathlib import Path
from loguru import logger as _loguru_logger


# ============================================================
# 初始化
# ============================================================

def setup_logger(
    log_dir: str = "logs",
    retention_days: int = 30,
    console_level: str = "INFO",
    file_level: str = "DEBUG",
) -> "loguru.logger":
    """
    配置 Loguru 集中式日志系统

    Args:
        log_dir: 日志文件存储根目录
        retention_days: 日志保留天数（默认 30 天）
        console_level: 控制台最低输出级别
        file_level: 文件最低记录级别
    """
    # Windows 控制台 UTF-8 模式
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    # ---- 清除默认 handler ----
    _loguru_logger.remove()

    # ---- 获取项目根目录 ----
    project_root = Path(__file__).parent.parent.parent.resolve()
    log_path = project_root / log_dir
    error_log_path = log_path / "error"

    # 自动创建目录
    log_path.mkdir(parents=True, exist_ok=True)
    error_log_path.mkdir(parents=True, exist_ok=True)

    # ---- 控制台格式（5 级彩色）----
    # level icon: DEBUG🔵 INFO🟢 WARNING🟡 ERROR🔴 CRITICAL💥
    console_format = (
        "<green>{time:HH:mm:ss}</green>"
        " <level>[{level}]</level>"
        " {level.icon} "
        "<level>{message}</level>"
    )

    _loguru_logger.add(
        sys.stdout,
        level=console_level,
        format=console_format,
        colorize=True,
        backtrace=False,
        diagnose=False,
    )

    # ---- 常规日志：按天滚动 + 30 天保留 ----
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "[{level:<7}] | "
        "{level.icon} {message}"
        "{exception}"
    )

    main_log_file = log_path / "app_{time:YYYY-MM-DD}.log"

    _loguru_logger.add(
        str(main_log_file),
        level=file_level,
        format=file_format,
        rotation="00:00",
        retention=f"{retention_days} days",
        compression="zip",
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )

    # ---- ERROR 日志：单独归档到 logs/error/ ----
    error_log_file = error_log_path / "app_{time:YYYY-MM-DD}.log"

    _loguru_logger.add(
        str(error_log_file),
        level="ERROR",
        format=file_format,
        rotation="00:00",
        retention=f"{retention_days} days",
        compression="zip",
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
        enqueue=True,
        filter=lambda record: record["level"].no >= logging.ERROR,
    )

    # ---- 拦截标准 logging 流量（第三方库）----
    class _LoguruHandler(logging.Handler):
        def emit(self, record: logging.LogRecord):
            try:
                level_name = record.levelname.upper()
                icon_map = {
                    "DEBUG": "🔵", "INFO": "🟢",
                    "WARNING": "🟡", "ERROR": "🔴", "CRITICAL": "💥",
                }
                icon = icon_map.get(level_name, "ℹ️")
                msg = self.format(record)
                if record.levelno >= logging.CRITICAL:
                    _loguru_logger.critical(f"{icon} {msg}")
                elif record.levelno >= logging.ERROR:
                    _loguru_logger.error(f"{icon} {msg}")
                elif record.levelno >= logging.WARNING:
                    _loguru_logger.warning(f"{icon} {msg}")
                elif record.levelno >= logging.INFO:
                    _loguru_logger.info(f"{icon} {msg}")
                else:
                    _loguru_logger.debug(f"{icon} {msg}")
            except Exception:
                self.handleError(record)

    handler = _LoguruHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.DEBUG)

    # ---- 启动横幅 ----
    _loguru_logger.info("=" * 58)
    _loguru_logger.info("🚀 日志系统初始化完成")
    _loguru_logger.info(f"   控制台级别: {console_level}")
    _loguru_logger.info(f"   文件级别: {file_level}")
    _loguru_logger.info(f"   日志目录: {log_path}")
    _loguru_logger.info(f"   错误日志: {error_log_path}")
    _loguru_logger.info(f"   保留天数: {retention_days} 天")
    _loguru_logger.info("=" * 58)

    return _loguru_logger


# ============================================================
# 全局单例导出
# ============================================================

# 预初始化（模块级别），确保任何地方 import 都能拿到已配置的 logger
# 首次 import 时自动 setup
setup_logger(retention_days=30, console_level="INFO", file_level="DEBUG")

# 对外导出同一实例
logger = _loguru_logger


# ============================================================
# 便捷日志函数（业务埋点专用）
# ============================================================

def log_agent_task_received(agent_name: str, task_type: str, task_detail: str = ""):
    """Agent 接收任务 → INFO"""
    detail = f" | 任务详情: {task_detail}" if task_detail else ""
    logger.info(f"📋 Agent[{agent_name}] 接收任务 | type={task_type}{detail}")


def log_agent_task_completed(agent_name: str, task_type: str, output_preview: str = ""):
    """Agent 任务完成 → INFO (success icon via logger.success)"""
    preview = f" | 输出预览: {output_preview[:80]}..." if output_preview else ""
    logger.success(f"✅ Agent[{agent_name}] 任务完成 | type={task_type}{preview}")


def log_rag_verification(
    entity: str,
    match_type: str,
    confidence: float,
    paths: list = None,
    graph_edges_checked: int = 0,
):
    """RAG 图谱校验 → DEBUG（详细信息）"""
    icon_map = {"exact": "✅", "reverse": "🔄", "path": "🛤️", "none": "❌"}
    icon = icon_map.get(match_type, "❓")
    path_info = ""
    if paths:
        path_str = " → ".join(
            f"{p['head']}[{p['relation']}] {p['tail']}" for p in paths[:3]
        )
        path_info = f" | 路径: {path_str}"

    logger.debug(
        f"{icon} RAG图谱校验 | {entity} | "
        f"match={match_type} | conf={confidence:.3f} | "
        f"edges={graph_edges_checked}{path_info}"
    )


def log_critique_reject(
    hallucination_content: str,
    reject_reason: str,
    confidence: float,
    suggested_fix: str = "",
):
    """杏林纠错官拦截 → WARNING（核心防幻觉）"""
    fix_info = f" | 修正建议: {suggested_fix[:60]}..." if suggested_fix else ""

    logger.warning(
        f"⚠️ 杏林纠错官 [REJECT] | "
        f"置信度={confidence:.3f} | "
        f"拦截内容: {hallucination_content[:100]} | "
        f"拒绝原因: {reject_reason[:80]}{fix_info}"
    )


def log_api_error(
    api_name: str,
    error_type: str,
    error_detail: str,
    retry_count: int = 0,
):
    """API 异常 → ERROR"""
    retry_info = f" | 重试次数: {retry_count}" if retry_count else ""
    logger.error(
        f"❌ API异常[{api_name}] | type={error_type} | "
        f"detail: {error_detail[:200]}{retry_info}"
    )


def log_state_transition(from_state: str, to_state: str, trigger: str = ""):
    """流程状态转换 → INFO"""
    trigger_info = f" | trigger={trigger}" if trigger else ""
    logger.info(f"🔄 状态转换 | {from_state} → {to_state}{trigger_info}")
