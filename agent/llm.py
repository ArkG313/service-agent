"""
LLM 客户端封装 —— 统一管理 OpenAI API 调用。
"""

from __future__ import annotations

import logging
from typing import Any

from openai import OpenAI

from config.settings import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM 客户端,支持普通对话与工具调用。"""

    def __init__(self) -> None:
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.llm_base_url,
            )
        return self._client

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict] | None = None,
    ) -> dict[str, Any]:
        """
        同步聊天调用。

        Returns:
            {"content": str, "tool_calls": list}
        """
        try:
            kwargs: dict[str, Any] = {
                "model": settings.llm_model,
                "messages": messages,
                "temperature": settings.llm_temperature,
                "max_tokens": settings.llm_max_tokens,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message

            result: dict[str, Any] = {
                "content": message.content or "",
                "tool_calls": [],
            }
            if message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                    for tc in message.tool_calls
                ]
            return result
        except Exception as e:
            logger.error("LLM 调用失败: %s", e, exc_info=True)
            return {"content": f"抱歉,服务暂时不可用: {e}", "tool_calls": []}


llm_client = LLMClient()
