"""
工具基类与注册中心。

继承 BaseTool,实现 name/description/parameters/execute 即可自动注册。
"""

from __future__ import annotations

import abc
import logging
from typing import Any

logger = logging.getLogger(__name__)


class BaseTool(abc.ABC):
    """工具基类。"""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """工具名称(英文)。"""

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """工具描述。"""

    @property
    def parameters(self) -> dict[str, Any]:
        """参数 JSON Schema。"""
        return {"type": "object", "properties": {}}

    @abc.abstractmethod
    def execute(self, **kwargs: Any) -> str:
        """执行工具,返回结果字符串。"""

    def to_openai_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """工具注册中心。"""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool
        logger.info("已注册工具: %s", tool.name)

    def register_many(self, tools: list[BaseTool]) -> None:
        for tool in tools:
            self.register(tool)

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def execute(self, name: str, **kwargs: Any) -> str:
        tool = self._tools.get(name)
        if tool is None:
            return f"错误: 工具 '{name}' 不存在"
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            logger.error("工具 %s 执行失败: %s", name, e, exc_info=True)
            return f"工具执行出错: {e}"

    def get_openai_tools_schema(self) -> list[dict[str, Any]]:
        return [t.to_openai_schema() for t in self._tools.values()]

    def get_tools_description(self) -> str:
        if not self._tools:
            return ""
        return "\n".join(f"- {t.name}: {t.description}" for t in self._tools.values())

    def list_names(self) -> list[str]:
        return list(self._tools.keys())
