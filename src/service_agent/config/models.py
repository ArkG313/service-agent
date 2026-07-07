"""
数据模型定义。
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    role: Role
    content: str = ""
    name: str | None = None
    tool_calls: list[dict] | None = None


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = Field(default=None, description="会话 ID,为空则新建")


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    tool_used: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
