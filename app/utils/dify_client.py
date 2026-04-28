"""
============================================
Dify 工作流调用客户端
============================================
功能：
  1. 调用 Dify 中医多智能体工作流（5个专家切换）
  2. 支持 sync/async 两种调用模式
  3. 未配置Dify时降级到原LLM直调模式

⚠️ 免责声明：所有输出仅供教育学习参考，非医疗建议。
============================================
"""

import os
import json
import time
import uuid
from typing import Optional, Dict, Any

import httpx
from dotenv import load_dotenv
from app.core.logger import logger

load_dotenv()


class DifyClient:
    """Dify 工作流调用客户端（单例）"""

    _instance: Optional['DifyClient'] = None

    def __init__(self):
        self.api_url = os.getenv("DIFY_API_URL", "").rstrip("/")
        self.api_key = os.getenv("DIFY_API_KEY", "")
        self.app_id = os.getenv("DIFY_APP_ID", "")
        self.enabled = bool(self.api_url and self.api_key)
        self.timeout = float(os.getenv("DIFY_TIMEOUT", "60"))
        self._client = None

        if self.enabled:
            logger.info(f"✅ Dify客户端已启用 | API: {self.api_url}")
        else:
            logger.warning("⚠️ Dify未配置（DIFY_API_URL/DIFY_API_KEY未设置），将降级到原LLM直调模式")

    @classmethod
    def get_instance(cls) -> 'DifyClient':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

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

    def is_enabled(self) -> bool:
        return self.enabled

    async def chat_with_workflow(
        self,
        expert_type: str,
        question: str,
        user: str = "tcm-learning-agent",
    ) -> Dict[str, Any]:
        """
        调用 Dify 中医多智能体工作流

        Args:
            expert_type: 专家类型
                - 中医通识专家
                - 针灸推拿专家
                - 中药方剂专家
                - 中医诊断专家
                - 养生保健专家
            question: 用户问题
            user: 用户标识

        Returns:
            Dify API 响应字典
        """
        if not self.enabled:
            return {"error": "Dify未启用"}

        request_id = f"dify-{uuid.uuid4().hex[:8]}"

        # Dify workflow blocking 模式
        payload = {
            "inputs": {
                "expert_select": expert_type,
                "user_question": question,
            },
            "response_mode": "blocking",
            "user": user,
        }

        url = f"{self.api_url}/workflows/run"

        try:
            logger.info(f"🔄 Dify工作流调用 | req={request_id} | expert={expert_type}")
            start = time.time()

            response = await self.client.post(url, json=payload)
            elapsed = (time.time() - start) * 1000

            if not response.is_success:
                logger.error(f"❌ Dify调用失败 | req={request_id} | status={response.status_code} | body={response.text[:200]}")
                return {"error": f"Dify API error: {response.status_code}", "body": response.text[:200]}

            result = response.json()
            logger.info(f"✅ Dify工作流完成 | req={request_id} | elapsed={elapsed:.0f}ms")

            # 解析 Dify workflow 输出
            # 格式: {"data": {"outputs": {"answer": "..."}}}
            outputs = result.get("data", {}).get("outputs", {})

            # 提取最终回答（answer节点输出）
            answer_text = outputs.get("answer", "") or str(outputs)

            return {
                "success": True,
                "answer": answer_text,
                "outputs": outputs,
                "elapsed_ms": elapsed,
            }

        except httpx.TimeoutException:
            logger.error(f"❌ Dify调用超时 | req={request_id} | timeout={self.timeout}s")
            return {"error": f"Dify调用超时({self.timeout}s)"}
        except Exception as e:
            logger.error(f"❌ Dify调用异常 | req={request_id} | {type(e).__name__}: {e}")
            return {"error": f"Dify调用异常: {e}"}

    async def chat_with_workflow_stream(
        self,
        expert_type: str,
        question: str,
        user: str = "tcm-learning-agent",
    ):
        """
        调用 Dify 工作流（流式模式，返回 AsyncGenerator）
        """
        if not self.enabled:
            yield {"error": "Dify未启用"}
            return

        request_id = f"dify-stream-{uuid.uuid4().hex[:8]}"

        payload = {
            "inputs": {
                "expert_select": expert_type,
                "user_question": question,
            },
            "response_mode": "streaming",
            "user": user,
        }

        url = f"{self.api_url}/workflows/run"

        try:
            logger.info(f"🔄 Dify工作流(流式) | req={request_id} | expert={expert_type}")
            async with self.client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data_str = line[5:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        # 流式返回: {"event": "message", "data": {"content": "..."}}
                        event = chunk.get("event", "")
                        if event == "message":
                            content = chunk.get("data", {}).get("content", "")
                            yield {"success": True, "content": content, "done": False}
                    except json.JSONDecodeError:
                        continue
                yield {"success": True, "content": "", "done": True}
        except Exception as e:
            logger.error(f"❌ Dify流式调用异常 | req={request_id} | {e}")
            yield {"error": str(e), "done": True}

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


# ==================== 便捷函数 ====================

def get_dify_client() -> DifyClient:
    return DifyClient.get_instance()


async def call_expert(expert_type: str, question: str) -> Dict[str, Any]:
    """调用指定专家类型的Dify工作流"""
    client = get_dify_client()
    return await client.chat_with_workflow(expert_type, question)