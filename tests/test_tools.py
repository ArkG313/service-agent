"""
工具系统测试。
"""

from tools.base import BaseTool, ToolRegistry


class MockTool(BaseTool):
    @property
    def name(self) -> str:
        return "mock_tool"

    @property
    def description(self) -> str:
        return "测试工具"

    @property
    def parameters(self) -> dict:
        return {"type": "object", "properties": {"text": {"type": "string"}}}

    def execute(self, text: str = "", **kwargs) -> str:
        return f"echo: {text}"


def test_tool_registry_register():
    registry = ToolRegistry()
    registry.register(MockTool())
    assert "mock_tool" in registry.list_names()


def test_tool_registry_execute():
    registry = ToolRegistry()
    registry.register(MockTool())
    result = registry.execute("mock_tool", text="hello")
    assert result == "echo: hello"


def test_tool_unknown():
    registry = ToolRegistry()
    result = registry.execute("nonexistent")
    assert "不存在" in result


def test_get_default_tools():
    from tools.builtin import get_default_tools

    tools = get_default_tools()
    names = [t.name for t in tools]
    assert "get_current_time" in names
    assert "query_order_status" in names
