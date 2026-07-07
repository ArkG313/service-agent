"""
RAG 检索模块 —— 基于 ChromaDB 的知识库检索。

功能:文档加载 / 分块 / 向量化存储 / 语义检索 / 上下文拼接
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from config.settings import settings

logger = logging.getLogger(__name__)


class RAGManager:
    """RAG 检索管理器,懒初始化,不影响基本对话。"""

    def __init__(self) -> None:
        self._chroma: Any = None
        self._collection: Any = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        try:
            import chromadb

            path = settings.chroma_path
            path.mkdir(parents=True, exist_ok=True)
            self._chroma = chromadb.PersistentClient(path=str(path))
            self._collection = self._chroma.get_or_create_collection(
                name=settings.chroma_collection_name
            )
            self._initialized = True

            if self._collection.count() == 0:
                self._load_from_knowledge_base()
        except Exception as e:
            logger.warning("RAG 初始化失败(不影响基本对话): %s", e)
            self._initialized = False

    def _load_from_knowledge_base(self) -> None:
        kb_path = settings.knowledge_base_path
        if not kb_path.exists():
            return
        docs = self._load_documents(kb_path)
        if not docs:
            return
        chunks = self._split_documents(docs)
        if chunks:
            self._add_chunks(chunks)
            logger.info("知识库已加载: %d 个分块", self._collection.count())

    def _load_documents(self, directory: Path) -> list[dict[str, str]]:
        documents: list[dict[str, str]] = []
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            suffix = path.suffix.lower()
            try:
                if suffix in (".txt", ".md"):
                    text = path.read_text(encoding="utf-8")
                elif suffix == ".pdf":
                    text = self._load_pdf(path)
                else:
                    continue
                if text.strip():
                    documents.append({"content": text, "source": str(path)})
            except Exception as e:
                logger.error("加载文档失败 %s: %s", path, e)
        return documents

    def _load_pdf(self, path: Path) -> str:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def _split_documents(self, documents: list[dict[str, str]]) -> list[dict[str, str]]:
        chunks: list[dict[str, str]] = []
        chunk_size = settings.rag_chunk_size
        overlap = settings.rag_chunk_overlap
        for doc in documents:
            text = doc["content"]
            source = doc["source"]
            start, idx = 0, 0
            while start < len(text):
                chunk_text = text[start : start + chunk_size].strip()
                if chunk_text:
                    chunks.append({
                        "content": chunk_text,
                        "source": source,
                        "chunk_id": f"{Path(source).stem}_{idx}",
                    })
                start += chunk_size - overlap
                idx += 1
        return chunks

    def _add_chunks(self, chunks: list[dict[str, str]]) -> None:
        self._collection.add(
            ids=[c["chunk_id"] for c in chunks],
            documents=[c["content"] for c in chunks],
            metadatas=[{"source": c["source"]} for c in chunks],
        )

    def search(self, query: str, top_k: int | None = None) -> tuple[str, list[str]]:
        """语义检索,返回 (上下文文本, 来源列表)。"""
        self._ensure_initialized()
        if not self._initialized or not self._collection:
            return "", []
        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k or settings.rag_top_k,
            )
            docs = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            if not docs:
                return "", []
            parts, sources = [], []
            for i, doc in enumerate(docs):
                source = metadatas[i].get("source", "未知") if i < len(metadatas) else "未知"
                parts.append(f"[{i + 1}] (来源: {source})\n{doc}")
                if source not in sources:
                    sources.append(source)
            return "\n\n".join(parts), sources
        except Exception as e:
            logger.error("RAG 检索失败: %s", e)
            return "", []

    def reload(self) -> None:
        """重新加载知识库。"""
        self._ensure_initialized()
        if not self._initialized:
            return
        self._chroma.delete_collection(settings.chroma_collection_name)
        self._collection = self._chroma.get_or_create_collection(
            name=settings.chroma_collection_name
        )
        self._load_from_knowledge_base()

    def get_stats(self) -> dict[str, Any]:
        self._ensure_initialized()
        if not self._initialized:
            return {"initialized": False, "chunk_count": 0}
        return {
            "initialized": True,
            "chunk_count": self._collection.count(),
            "collection": settings.chroma_collection_name,
        }


rag_manager = RAGManager()
