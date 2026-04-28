"""
============================================
中医知识库文档加载 & 语义分块模块
============================================
功能：
  1. 加载中医教材 Markdown 文件
  2. 按标题层级（# / ## / ###）进行语义切分
  3. 保留层级元数据（章节路径），供 RAG 检索时定位

设计理念：
  中医教材具有严格的章节层级结构（章→节→知识点），
  按 Markdown 标题切分比固定长度切分更能保持语义完整性。

⚠️ 免责声明：所有加载内容仅供教育学习参考，非医疗建议。
============================================
"""

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

import yaml
from loguru import logger


# ============================================================
# 数据模型：文档分块
# ============================================================

@dataclass
class TcmDocumentChunk:
    """
    中医文档分块数据模型

    每个分块对应 Markdown 中的一个标题段落，
    保留了完整的层级路径信息。

    Attributes:
        content: 分块文本内容
        source_file: 来源文件名
        chapter_path: 章节层级路径，如 ["第一章 中医学的哲学基础", "第一节 阴阳学说"]
        heading_level: 标题层级（1=章, 2=节, 3=知识点）
        keywords: 从 config.yaml 映射的关键词
        metadata: 额外元数据
    """
    content: str
    source_file: str = ""
    chapter_path: List[str] = field(default_factory=list)
    heading_level: int = 1
    keywords: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_langchain_document(self):
        """
        转换为 LangChain Document 格式（供向量库使用）

        Returns:
            langchain.schema.Document: 包含 page_content 和 metadata
        """
        from langchain.schema import Document

        return Document(
            page_content=self.content,
            metadata={
                "source": self.source_file,
                "chapter_path": " > ".join(self.chapter_path),
                "heading_level": self.heading_level,
                "keywords": ", ".join(self.keywords),
                **self.metadata,
            }
        )


# ============================================================
# 核心类：中医文档加载器
# ============================================================

class TcmDocLoader:
    """
    中医教材 Markdown 文档加载器

    特点：
      - 按 Markdown 标题层级（#/##/###）进行语义切分
      - 自动映射 config.yaml 中的章节关键词
      - 保留章节路径，方便检索定位
      - 支持单个文件或整个目录批量加载

    使用示例：
        >>> loader = TcmDocLoader(config_path="config.yaml")
        >>> chunks = loader.load_directory("./data/knowledge_base/中医基础理论")
        >>> print(f"加载 {len(chunks)} 个知识分块")
    """

    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化加载器

        Args:
            config_path: config.yaml 路径，用于读取课程大纲关键词映射
        """
        self.config = self._load_config(config_path)
        self._keyword_map = self._build_keyword_map()

    def _load_config(self, config_path: str) -> dict:
        """加载 config.yaml 中的课程配置"""
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        logger.warning(f"config.yaml 未找到: {config_path}，使用空配置")
        return {}

    def _build_keyword_map(self) -> dict:
        """
        构建章节关键词映射表

        从 config.yaml 的 course.syllabus 中提取，
        返回 {"ch01": ["阴阳", "五行", ...], "ch02": [...]} 格式的映射。
        """
        keyword_map = {}
        syllabus = self.config.get("course", {}).get("syllabus", [])
        for ch in syllabus:
            keyword_map[ch.get("id", "")] = ch.get("keywords", [])
            # 同时用标题做模糊匹配
            keyword_map[ch.get("title", "")] = ch.get("keywords", [])
        return keyword_map

    def _match_keywords(self, text: str) -> List[str]:
        """
        从文本中匹配 config.yaml 定义的关键词

        Args:
            text: 待匹配的文本

        Returns:
            匹配到的关键词列表
        """
        matched = []
        for key, keywords in self._keyword_map.items():
            for kw in keywords:
                if kw in text:
                    matched.append(kw)
        return list(set(matched))  # 去重

    # ============================================================
    # Markdown 语义切分核心
    # ============================================================

    def _split_markdown_by_headers(self, markdown_text: str, source_file: str = "") -> List[TcmDocumentChunk]:
        """
        按 Markdown 标题层级进行语义切分

        切分规则：
          - 遇到 #（一级标题）开始新章节
          - 遇到 ##（二级标题）开始新小节
          - 遇到 ###（三级标题）开始新知识点
          - 同级标题之间的内容归入该分块
          - 保留完整的层级路径（如"第一章 > 第一节 > 阴阳的基本概念"）

        Args:
            markdown_text: Markdown 原始文本
            source_file: 来源文件名

        Returns:
            TcmDocumentChunk 列表
        """
        chunks = []
        current_path = []  # 当前层级路径栈
        current_level = 0  # 当前标题层级
        current_content_lines = []  # 当前分块内容行

        lines = markdown_text.split("\n")

        for line in lines:
            # 检测标题行
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if header_match:
                # 保存上一个分块
                content = "\n".join(current_content_lines).strip()
                if content:
                    keywords = self._match_keywords(content)
                    chunks.append(TcmDocumentChunk(
                        content=content,
                        source_file=source_file,
                        chapter_path=list(current_path),
                        heading_level=current_level,
                        keywords=keywords,
                    ))

                # 开始新分块
                level = len(header_match.group(1))  # # 的数量
                title = header_match.group(2).strip()

                # 更新层级路径栈
                # 如果新标题层级 <= 当前层级，弹出栈顶
                while current_path and level <= current_level:
                    current_path.pop()

                current_path.append(title)
                current_level = level
                current_content_lines = [line]  # 标题本身也放入内容

            else:
                # 普通文本行，追加到当前分块
                current_content_lines.append(line)

        # 保存最后一个分块
        content = "\n".join(current_content_lines).strip()
        if content:
            keywords = self._match_keywords(content)
            chunks.append(TcmDocumentChunk(
                content=content,
                source_file=source_file,
                chapter_path=list(current_path),
                heading_level=current_level,
                keywords=keywords,
            ))

        return chunks

    # ============================================================
    # 文件加载入口
    # ============================================================

    def load_file(self, file_path: str) -> List[TcmDocumentChunk]:
        """
        加载单个 Markdown 文件

        Args:
            file_path: 文件路径

        Returns:
            TcmDocumentChunk 列表
        """
        path = Path(file_path)
        if not path.exists():
            logger.error(f"文件不存在: {file_path}")
            return []

        if path.suffix.lower() not in (".md", ".markdown"):
            logger.warning(f"跳过非Markdown文件: {file_path}")
            return []

        logger.info(f"📄 加载文件: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = self._split_markdown_by_headers(text, source_file=path.name)
        logger.info(f"  ✅ 切分为 {len(chunks)} 个知识分块")
        return chunks

    def load_directory(self, dir_path: str) -> List[TcmDocumentChunk]:
        """
        批量加载目录下所有 Markdown 文件

        Args:
            dir_path: 目录路径

        Returns:
            所有文件的 TcmDocumentChunk 合并列表
        """
        all_chunks = []
        dir_path = Path(dir_path)

        if not dir_path.exists():
            logger.error(f"目录不存在: {dir_path}")
            return []

        for md_file in sorted(dir_path.rglob("*.md")):
            chunks = self.load_file(str(md_file))
            all_chunks.extend(chunks)

        logger.info(f"📚 目录加载完成: {len(all_chunks)} 个知识分块，来自 {dir_path}")
        return all_chunks
