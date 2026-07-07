"""
智能客服 Agent —— 核心编排逻辑。

工作流:
1. 接收用户输入
2. RAG 知识库检索(可选)
3. 调用 LLM(可能触发工具调用)
4. 执行工具,将结果回传给 LLM
5. 返回最终回复
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field

from agent.llm import llm_client
from agent.memory import memory_manager
from config.models import ChatResponse, Message, Role
from config.settings import settings
from rag.retriever import rag_manager
from tools.base import ToolRegistry
from tools.builtin import get_default_tools

logger = logging.getLogger(__name__)


@dataclass
class ServiceAgent:
    """智能客服 Agent。"""

    registry: ToolRegistry = field(default_factory=ToolRegistry)
    _system_prompt: str = ""

    def __post_init__(self) -> None:
        self.registry.register_many(get_default_tools())
        self._system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        tools_desc = self.registry.get_tools_description()
        prompt = settings.system_prompt
        if tools_desc:
            prompt += f"\n\n你可以使用以下工具:\n{tools_desc}"
        prompt += (
            "\n\n注意:\n"
            "1. 优先参考知识库内容回答。\n"
            "2. 不确定时如实告知并建议转人工客服。\n"
            "3. 回答简洁、专业、有礼貌。"
        )
        return prompt

    def chat(self, user_message: str, session_id: str | None = None) -> ChatResponse:
        """处理用户消息,返回 Agent 回复。"""
        if session_id is None:
            session_id = str(uuid.uuid4())

        # 1. RAG 检索
        rag_context, sources = rag_manager.search(user_message)

        # 2. 构建增强消息
        enhanced = user_message
        if rag_context:
            enhanced = (
                f"用户问题: {user_message}\n\n"
                f"知识库参考内容:\n{rag_context}"
            )

        # 3. 记录用户消息
        memory_manager.add(session_id, Message(role=Role.USER, content=enhanced))

        # 4. LLM 第一轮调用
        messages = [m.model_dump() for m in memory_manager.get_messages_with_system(session_id, self._system_prompt)]
        tools = self.registry.get_openai_tools_schema()
        result = llm_client.chat(messages, tools=tools if tools else None)

        tools_used: list[str] = []

        # 5. 如果触发工具调用,执行并回传
        if result["tool_calls"]:
            memory_manager.add(session_id, Message(
                role=Role.ASSISTANT,
                content=result["content"],
                tool_calls=result["tool_calls"],
            ))
            for tc in result["tool_calls"]:
                try:
                    tool_args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                except json.JSONDecodeError:
                    tool_args = {}
                logger.info("执行工具: %s, 参数: %s", tc["name"], tool_args)
                tool_result = self.registry.execute(tc["name"], **tool_args)
                tools_used.append(tc["name"])
                memory_manager.add(session_id, Message(
                    role=Role.TOOL, content=tool_result, name=tc["name"]
                ))

            # 6. LLM 第二轮调用
            messages = [m.model_dump() for m in memory_manager.get_messages_with_system(session_id, self._system_prompt)]
            result = llm_client.chat(messages, tools=None)

        # 7. 记录最终回复
        memory_manager.add(session_id, Message(role=Role.ASSISTANT, content=result["content"]))

        return ChatResponse(
            session_id=session_id,
            reply=result["content"],
            tool_used=tools_used,
            sources=sources,
        )

    def reset_session(self, session_id: str) -> None:
        memory_manager.clear(session_id)


service_agent = ServiceAgent()
