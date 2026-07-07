"""
会话记忆管理 —— 基于内存的多会话对话历史存储。
"""

from __future__ import annotations

from collections import defaultdict

from config.models import Message, Role
from config.settings import settings


class MemoryManager:
    """管理多会话的对话记忆,按 session_id 隔离。"""

    def __init__(self, max_messages: int | None = None) -> None:
        self._max = max_messages or settings.max_memory_messages
        self._sessions: dict[str, list[Message]] = defaultdict(list)

    def add(self, session_id: str, message: Message) -> None:
        self._sessions[session_id].append(message)
        self._truncate(session_id)

    def get_history(self, session_id: str) -> list[Message]:
        return list(self._sessions.get(session_id, []))

    def get_messages_with_system(self, session_id: str, system_prompt: str) -> list[Message]:
        messages = [Message(role=Role.SYSTEM, content=system_prompt)]
        messages.extend(self.get_history(session_id))
        return messages

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def list_sessions(self) -> list[str]:
        return list(self._sessions.keys())

    def get_session_info(self, session_id: str) -> dict:
        history = self.get_history(session_id)
        return {
            "session_id": session_id,
            "message_count": len(history),
            "exists": session_id in self._sessions,
        }

    def _truncate(self, session_id: str) -> None:
        history = self._sessions[session_id]
        if len(history) > self._max:
            self._sessions[session_id] = history[-self._max :]


memory_manager = MemoryManager()
