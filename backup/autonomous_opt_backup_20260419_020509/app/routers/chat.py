"""
============================================
核心API路由：/api/v1/chat/learning
===========================================
功能：
  1. 接收学习请求，调度Crew执行
  2. 支持SSE流式响应，实时推送Agent工作过程
  3. 返回结构化的学习画像、资源包、审校报告、学习路径

SSE事件类型：
  - step: Agent执行步骤更新（如"正在检索..."、"杏林纠错官审校中..."）
  - result: 最终完整结果
  - error: 错误信息

前端可据此制作酷炫的"Agent工作台"动画。

⚠️ 基于讯飞星火 v3.5/4.0 驱动
⚠️ 免责声明：所有输出仅供教育学习参考，非医疗建议
============================================
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from queue import Queue

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from app.models.schemas import (
    LearningRequest,
    ResourceResponse,
    SSEEvent,
    CrewStatus,
    CritiqueVerdict,
)
from app.crew.tcm_learning_crew import TcmLearningCrew, CrewState
from app.middleware.unified_response import unified_response


router = APIRouter(prefix="/api/v1/chat", tags=["中医学习智能体"])


# ============================================================
# 主接口：流式学习交互
# ============================================================

@router.post("/learning")
async def learning_chat(request: LearningRequest):
    """
    核心学习交互接口（SSE流式响应）

    根据用户输入，调度多智能体Crew执行学习任务，
    并通过SSE实时推送Agent工作过程。

    Args:
        request: 学习请求体

    Returns:
        StreamingResponse: SSE流式响应

    SSE事件示例：
        event: step
        data: {"step": "profile_building", "message": "开始构建学习画像...", "state": "building_profile"}

        event: step
        data: {"step": "critiquing", "message": "杏林纠错官正在审校...", "state": "critiquing"}

        event: result
        data: {"task_type": "generate_resources", "status": "completed", "profile": {...}, "resources": {...}}

        event: error
        data: {"message": "审校多次未通过", "state": "failed"}
    """
    # 创建SSE事件队列
    event_queue: Queue = Queue()

    # 创建Crew实例
    crew = TcmLearningCrew()

    # 注册步骤回调 → 将中间过程推入队列
    def on_step(step_name: str, step_data: Any, state: str, detailed_log: Optional[Dict] = None):
        event_data = {
            "step": step_name,
            "message": str(step_data)[:500] if isinstance(step_data, str) else step_name,
            "state": state,
            "detailed_log": detailed_log or {
                "thought": f"Agent {step_name} 正在处理...",
                "agent": step_name.split("_")[0] if "_" in step_name else step_name,
            },
        }
        event_queue.put(SSEEvent(event="step", data=event_data))

    crew.on_step(on_step)

    # 异步执行Crew（在后台线程中运行，避免阻塞）
    async def run_crew():
        try:
            result = await crew.run(
                user_messages=request.user_messages,
                task_type=request.task_type.value,
                profile_data=request.profile_data,
                knowledge_point=request.knowledge_point or "",
                resource_types=[rt.value for rt in request.resource_types] if request.resource_types else None,
            )
            # 将最终结果推入队列
            event_queue.put(SSEEvent(
                event="result",
                data=result,
            ))
        except Exception as e:
            logger.error(f"Crew执行异常: {e}")
            event_queue.put(SSEEvent(
                event="error",
                data={"message": str(e), "state": CrewState.FAILED.value},
            ))
        finally:
            # 发送结束标记
            event_queue.put(None)

    # 启动Crew任务
    crew_task = asyncio.create_task(run_crew())

    # SSE生成器
    async def event_generator():
        """SSE事件生成器，从队列中读取事件并格式化输出"""
        while True:
            # 非阻塞检查队列
            while not event_queue.empty():
                event = event_queue.get()

                if event is None:
                    # 结束标记
                    yield f"event: done\ndata: {{}}\n\n"
                    return

                # 格式化为SSE
                event_data = json.dumps({
                    "event": event.event,
                    "data": event.data,
                    "timestamp": event.timestamp.isoformat(),
                }, ensure_ascii=False)

                yield f"event: {event.event}\ndata: {event_data}\n\n"

            # 短暂等待，避免空转
            await asyncio.sleep(0.1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Nginx兼容
        },
    )


# ============================================================
# 非流式接口（备选，方便调试）
# ============================================================

@router.post("/learning/sync")
async def learning_chat_sync(request: LearningRequest) -> ResourceResponse:
    """
    同步学习交互接口（非流式，方便调试）

    与 /learning 功能相同，但不使用SSE，直接返回完整结果。

    Args:
        request: 学习请求体

    Returns:
        ResourceResponse: 完整的学习结果
    """
    crew = TcmLearningCrew()

    result = await crew.run(
        user_messages=request.user_messages,
        task_type=request.task_type.value,
        profile_data=request.profile_data,
        knowledge_point=request.knowledge_point or "",
        resource_types=[rt.value for rt in request.resource_types] if request.resource_types else None,
    )

    # 提取审校结论
    critique_verdict = None
    critique_text = str(result.get("critique_report") or "")
    if "[REJECT]" in critique_text:
        critique_verdict = CritiqueVerdict.REJECT
    elif "[WARN]" in critique_text:
        critique_verdict = CritiqueVerdict.WARN
    else:
        critique_verdict = CritiqueVerdict.APPROVE

    return ResourceResponse(
        task_type=request.task_type,
        status=CrewStatus(result.get("state", "idle")),
        profile=result.get("profile"),
        retrieval_report=str(result.get("retrieval_report", ""))[:500],
        resources=result.get("resources"),
        critique_report=str(result.get("critique_report", ""))[:500],
        critique_verdict=critique_verdict,
        learning_path=result.get("learning_path"),
        retry_count=result.get("retry_count", 0),
        errors=result.get("errors", []),
    )


# ============================================================
# 健康检查
# ============================================================

@router.get("/health")
async def health_check():
    """健康检查接口"""
    return unified_response(200, "服务正常", {
        "status": "healthy",
        "service": "tcm-ai-learning-agent",
        "llm": "iFlytek Spark (讯飞星火)",
        "framework": "CrewAI + FastAPI",
        "disclaimer": "⚠️ 仅供教育学习参考，非医疗建议",
    })
