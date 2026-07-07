"""
配置与记忆测试。
"""

from config.models import ChatRequest, ChatResponse, Message, Role
from config.settings import Settings
from agent.memory import MemoryManager


def test_settings_defaults():
    s = Settings()  # type: ignore[call-arg]
    assert s.llm_model == "gpt-4o-mini"
    assert s.rag_top_k == 3


def test_message_model():
    msg = Message(role=Role.USER, content="你好")
    assert msg.role == Role.USER
    assert msg.content == "你好"


def test_chat_request():
    req = ChatRequest(message="测试")
    assert req.message == "测试"
    assert req.session_id is None


def test_memory_add_and_get():
    mem = MemoryManager(max_messages=10)
    mem.add("s1", Message(role=Role.USER, content="你好"))
    mem.add("s1", Message(role=Role.ASSISTANT, content="你好!"))

    history = mem.get_history("s1")
    assert len(history) == 2
    assert history[0].content == "你好"


def test_memory_isolation():
    mem = MemoryManager(max_messages=10)
    mem.add("s1", Message(role=Role.USER, content="会话1"))
    mem.add("s2", Message(role=Role.USER, content="会话2"))
    assert len(mem.get_history("s1")) == 1
    assert len(mem.get_history("s2")) == 1


def test_memory_truncate():
    mem = MemoryManager(max_messages=3)
    for i in range(5):
        mem.add("s1", Message(role=Role.USER, content=f"消息{i}"))
    assert len(mem.get_history("s1")) == 3


def test_memory_with_system():
    mem = MemoryManager(max_messages=10)
    mem.add("s1", Message(role=Role.USER, content="你好"))
    messages = mem.get_messages_with_system("s1", "你是客服")
    assert len(messages) == 2
    assert messages[0].role == Role.SYSTEM
