# ============================================
# TCM AI Learning Agent — Dockerfile
# 基于 python:3.11-slim 生产镜像
# ============================================

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 防止中文 locale 警告
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# ---- 安装系统依赖（中医 PDF/文档处理需要）----
RUN apt-get update && apt-get install -y --no-install-recommends \
    # 文档处理
    poppler-utils \
    tesseract-ocr \
    libsm6 \
    libxext6 \
    libxrender1 \
    # 字体（中文 PDF 渲染）
    fonts-noto-cjk \
    # 压缩/网络
    gzip \
    curl \
    # 清理
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ---- 先复制依赖文件，利用 Docker 缓存 ----
COPY requirements.txt /app/requirements.txt

# ---- 安装 Python 依赖 ----
RUN pip install --no-cache-dir -r requirements.txt

# ---- 复制全量项目代码 ----
COPY . /app/

# ---- 创建日志目录（容器内）----
RUN mkdir -p /app/logs /app/logs/error

# ---- 暴露端口 ----
EXPOSE 8000

# ---- 健康检查 ----
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/chat/health || exit 1

# ---- 启动命令（生产级）----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
