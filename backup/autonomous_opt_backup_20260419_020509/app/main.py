"""
============================================
tcm-ai-learning-agent FastAPI 应用入口
===========================================
基于讯飞星火大模型驱动的中医教育多智能体系统

赛题：第十五届中国软件杯 A3
  基于大模型的个性化资源生成与学习多智能体系统开发

技术栈：
  - LLM: iFlytek 星火大模型 (Spark v3.5/4.0)
  - Agent Framework: CrewAI
  - Web Framework: FastAPI
  - RAG: ChromaDB + 中医知识图谱

开源致谢：
  - A-R007/Multi-Agent-Study-Assistant (MIT)
  - crewAIInc/crewAI-examples (MIT)
  - deacs11/CrewAI_Personalized_Learning_Path (MIT)
  - AI-HPC-Research-Team/TCM_knowledge_graph
  - OpenTCM

⚠️ 免责声明：本系统所有输出仅供教育学习参考，非医疗建议。
   如有健康问题请咨询专业中医师。
============================================
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化集中式日志系统（必须首先导入）
from app.core.logger import logger, setup_logger, log_state_transition
setup_logger()


# ============================================================
# 应用生命周期管理
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 应用生命周期

    startup:
      - 加载配置
      - 初始化向量库（如需要）
      - 日志启动信息

    shutdown:
      - 清理资源
    """
    # ---- Startup ----
    logger.info("=" * 60)
    logger.info("🚀 tcm-ai-learning-agent 启动中...")
    logger.info(f"   LLM: iFlytek 星火大模型 ({os.getenv('SPARK_API_VERSION', 'generalv3.5')})")
    logger.info(f"   Agent Framework: CrewAI")
    logger.info(f"   向量库: {os.getenv('CHROMA_PERSIST_DIR', './data/vector_db')}")
    logger.info(f"   调试模式: {os.getenv('APP_DEBUG', 'false')}")
    logger.info("=" * 60)

    # 检查讯飞星火API凭证
    if not os.getenv("SPARK_APP_ID"):
        logger.warning("⚠️ SPARK_APP_ID 未配置，请在 .env 文件中填写讯飞星火API凭证")
    else:
        logger.info("✅ 讯飞星火API凭证已配置")

    yield

    # ---- Shutdown ----
    logger.info("👋 tcm-ai-learning-agent 已关闭")


# ============================================================
# 创建 FastAPI 应用
# ============================================================

app = FastAPI(
    title="中医教育多智能体系统",
    description="""
## 🏥 基于讯飞星火大模型的中医教育多智能体系统

### 核心特性
- **多智能体协同**：6个CrewAI Agent深度协作
- **强防幻觉**：GraphRAG + 杏林纠错官双重校验
- **个性化生成**：6维度学习画像驱动
- **多模态资源**：5+种资源类型（含3D动画数据）

### Agent角色
1. 🎯 画像构建专家 — 6维度学习画像
2. 🔍 中医知识检索专家 — RAG + GraphRAG
3. 📚 资源生成专家 — 5+种多模态资源
4. 🗺️ 路径规划专家 — 个性化学习路径
5. 🧓 杏林纠错官 — 防幻觉审校
6. 🎭 协调调度专家 — 流程编排

### ⚠️ 免责声明
本系统所有输出仅供教育学习参考，**非医疗建议**。
如有健康问题请咨询专业中医师。
    """,
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "tcm-ai-learning-agent",
        "url": "https://github.com/your-repo/tcm-ai-learning-agent",
    },
    license_info={
        "name": "MIT",
    },
)


# ============================================================
# CORS 中间件（前端联调必需）
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React 开发服务器
        "http://localhost:5173",   # Vite 开发服务器
        "http://localhost:8080",   # Vue 开发服务器
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*" if os.getenv("APP_DEBUG", "false").lower() == "true" else None,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 鉴权中间件（必须放在 CORS 之后）
app.add_middleware(AuthMiddleware)

# 统一响应格式中间件
app.add_middleware(UnifiedResponseMiddleware)


# ============================================================
# 注册路由
# ============================================================

from app.routers.chat import router as chat_router
from app.middleware.auth import AuthMiddleware
from app.middleware.unified_response import UnifiedResponseMiddleware
app.include_router(chat_router)


# ============================================================
# 根路径
# ============================================================

@app.get("/")
async def root():
    """根路径 - 返回系统信息"""
    return unified_response(200, "服务正常", {
        "service": "tcm-ai-learning-agent",
        "version": "1.0.0",
        "description": "基于讯飞星火大模型的中医教育多智能体系统",
        "llm": f"iFlytek Spark ({os.getenv('SPARK_API_VERSION', 'generalv3.5')})",
        "framework": "CrewAI + FastAPI",
        "docs": "/docs",
        "health": "/api/v1/chat/health",
        "disclaimer": "⚠️ 仅供教育学习参考，非医疗建议",
    })


# ============================================================
# 启动入口（直接运行 python main.py）
# ============================================================

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    debug = os.getenv("APP_DEBUG", "false").lower() == "true"

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info",
    )
