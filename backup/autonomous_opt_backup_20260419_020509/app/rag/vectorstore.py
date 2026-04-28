"""
============================================
中医知识向量存储模块
============================================
功能：
  1. 封装 ChromaDB 持久化向量库
  2. 集成讯飞星火 Embedding 接口（优先）或本地 Embedding（备选）
  3. 提供增删改查 + 相似度检索接口

⚠️ 免责声明：所有检索内容仅供教育学习参考，非医疗建议。
============================================
"""

import os
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from loguru import logger


# ============================================================
# 讯飞星火 Embedding 封装
# ============================================================

class SparkEmbeddingFunction:
    """
    讯飞星火文本向量化封装

    实现chromadb要求的EmbeddingFunction接口，
    调用讯飞星火Embedding API将文本转为向量。

    如果讯飞API不可用，自动降级到本地sentence-transformers模型。

    使用示例：
        >>> ef = SparkEmbeddingFunction(
        ...     app_id="xxx", api_key="xxx", api_secret="xxx"
        ... )
        >>> vectors = ef(["阴阳学说是中医的哲学基础"])
    """

    def __init__(
        self,
        app_id: str = "",
        api_key: str = "",
        api_secret: str = "",
        fallback_model: str = "shibing624/text2vec-base-chinese",
    ):
        """
        Args:
            app_id: 讯飞Embedding APP_ID
            api_key: 讯飞Embedding API_KEY
            api_secret: 讯飞Embedding API_SECRET
            fallback_model: 降级使用的本地HuggingFace模型名
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.fallback_model = fallback_model
        self._fallback_ef = None  # 延迟加载

    def __call__(self, input: List[str]) -> List[List[float]]:
        """
        将文本列表转为向量列表（chromadb要求的方法签名）

        优先调用讯飞星火Embedding API，
        如果失败则降级到本地sentence-transformers模型。

        Args:
            input: 待向量化的文本列表

        Returns:
            对应的向量列表
        """
        # 尝试讯飞API
        if self.app_id and self.api_key and self.api_secret:
            try:
                return self._spark_embed(input)
            except Exception as e:
                logger.warning(f"讯飞Embedding调用失败，降级到本地模型: {e}")

        # 降级到本地模型
        return self._fallback_embed(input)

    def _spark_embed(self, texts: List[str]) -> List[List[float]]:
        """
        调用讯飞星火Embedding API

        使用HTTP接口调用，返回文本向量。

        Args:
            texts: 待向量化的文本列表

        Returns:
            向量列表
        """
        import httpx

        url = "https://knowledge-api.xf-yun.com/v1/emi/embeddings"
        auth_token = f"Bearer {self.api_key}:{self.api_secret}"

        # 构建请求体
        request_body = {
            "model": "emb-73s",
            "input": texts,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_token,
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=request_body, headers=headers)
            response.raise_for_status()
            result = response.json()

        # 提取向量
        embeddings = []
        for item in result.get("data", []):
            embeddings.append(item["embedding"])

        logger.info(f"✅ 讯飞Embedding成功: {len(texts)}条文本 → {len(embeddings)}个向量")
        return embeddings

    def _fallback_embed(self, texts: List[str]) -> List[List[float]]:
        """
        降级方案：使用本地sentence-transformers模型

        默认使用 shibing624/text2vec-base-chinese（中文语义向量模型），
        适合中医文本的语义相似度计算。

        Args:
            texts: 待向量化的文本列表

        Returns:
            向量列表
        """
        if self._fallback_ef is None:
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer(self.fallback_model)
                self._fallback_ef = model
                logger.info(f"✅ 本地Embedding模型加载成功: {self.fallback_model}")
            except ImportError:
                # 最终兜底：使用chromadb默认的all-MiniLM-L6-v2
                logger.warning("sentence-transformers未安装，使用chromadb默认Embedding")
                from chromadb.utils import embedding_functions
                self._fallback_ef = embedding_functions.DefaultEmbeddingFunction()

        if hasattr(self._fallback_ef, 'encode'):
            # SentenceTransformer
            vectors = self._fallback_ef.encode(texts, show_progress_bar=False)
            return vectors.tolist()
        else:
            # chromadb EmbeddingFunction
            return self._fallback_ef(texts)


# ============================================================
# 核心类：中医知识向量库
# ============================================================

class TcmVectorStore:
    """
    中医知识向量库（基于ChromaDB）

    特点：
      - 持久化存储，重启不丢数据
      - 支持讯飞星火Embedding（优先）+ 本地模型降级
      - 存储分块元数据（章节路径、关键词、来源文件）
      - 支持相似度检索 + 元数据过滤

    使用示例：
        >>> store = TcmVectorStore()
        >>> # 初始化知识库
        >>> store.add_documents(chunks)
        >>> # 检索
        >>> results = store.search("阴阳学说的基本内容", top_k=5)
    """

    def __init__(
        self,
        persist_dir: str = "./data/vector_db",
        collection_name: str = "tcm_knowledge",
        embedding_app_id: str = "",
        embedding_api_key: str = "",
        embedding_api_secret: str = "",
    ):
        """
        Args:
            persist_dir: ChromaDB 持久化目录
            collection_name: 集合名称
            embedding_app_id: 讯飞Embedding APP_ID
            embedding_api_key: 讯飞Embedding API_KEY
            embedding_api_secret: 讯飞Embedding API_SECRET
        """
        self.persist_dir = persist_dir
        self.collection_name = collection_name

        # 初始化Embedding函数
        self.embedding_fn = SparkEmbeddingFunction(
            app_id=embedding_app_id,
            api_key=embedding_api_key,
            api_secret=embedding_api_secret,
        )

        # 初始化ChromaDB客户端
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"description": "中医基础理论知识库 - 基于讯飞星火大模型驱动"}
        )

        logger.info(f"✅ 向量库初始化完成 | 集合: {collection_name} | 路径: {persist_dir}")

    def add_documents(self, chunks) -> None:
        """
        将文档分块添加到向量库

        Args:
            chunks: TcmDocumentChunk 列表（来自 doc_loader）
        """
        if not chunks:
            logger.warning("没有可添加的分块")
            return

        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{chunk.source_file}_{chunk.heading_level}_{i}"
            ids.append(chunk_id)
            documents.append(chunk.content)
            metadatas.append({
                "source": chunk.source_file,
                "chapter_path": " > ".join(chunk.chapter_path),
                "heading_level": chunk.heading_level,
                "keywords": ", ".join(chunk.keywords),
            })

        # 批量添加（ChromaDB单次上限建议 < 5000）
        batch_size = 500
        for start in range(0, len(ids), batch_size):
            end = start + batch_size
            self.collection.upsert(
                ids=ids[start:end],
                documents=documents[start:end],
                metadatas=metadatas[start:end],
            )

        logger.info(f"✅ 已添加 {len(ids)} 个分块到向量库")

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_keywords: Optional[List[str]] = None,
        filter_chapter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        相似度检索

        Args:
            query: 查询文本
            top_k: 返回最相似的k个结果
            filter_keywords: 按关键词过滤（OR逻辑）
            filter_chapter: 按章节路径过滤（包含匹配）

        Returns:
            检索结果列表，每项包含 content, metadata, distance
        """
        # 构建过滤条件
        where_filter = None
        conditions = []

        if filter_keywords:
            # ChromaDB的where条件：keywords包含任一关键词
            keyword_conditions = [
                {"keywords": {"$contains": kw}} for kw in filter_keywords
            ]
            if len(keyword_conditions) == 1:
                conditions.append(keyword_conditions[0])
            else:
                conditions.append({"$or": keyword_conditions})

        if filter_chapter:
            conditions.append({"chapter_path": {"$contains": filter_chapter}})

        if conditions:
            where_filter = conditions[0] if len(conditions) == 1 else {"$and": conditions}

        # 执行检索
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        # 格式化输出
        formatted = []
        if results and results["documents"]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                formatted.append({
                    "content": doc,
                    "metadata": meta,
                    "distance": dist,  # 距离越小越相似
                    "similarity": 1 - dist,  # 相似度 = 1 - 距离
                })

        logger.info(f"🔍 检索完成: query='{query[:30]}...' | 返回{len(formatted)}条结果")
        return formatted

    def get_collection_stats(self) -> Dict[str, Any]:
        """获取向量库统计信息"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_dir": self.persist_dir,
        }
