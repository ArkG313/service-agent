"""
配置模块 —— 使用 pydantic-settings 从 .env 文件加载配置。
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置,从 .env 自动加载。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 2048
    llm_base_url: str = "https://api.openai.com/v1"

    # RAG
    chroma_persist_path: str = "./data/vector_db"
    chroma_collection_name: str = "service_knowledge"
    knowledge_base_dir: str = "./data/knowledge_base"
    rag_top_k: int = 3
    rag_chunk_size: int = 500
    rag_chunk_overlap: int = 50

    # 服务
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Agent
    max_memory_messages: int = 20
    system_prompt: str = "你是一个专业的客服助手，请友好、准确地回答用户问题。"

    @property
    def knowledge_base_path(self) -> Path:
        return Path(self.knowledge_base_dir)

    @property
    def chroma_path(self) -> Path:
        return Path(self.chroma_persist_path)


settings = Settings()  # type: ignore[call-arg]
