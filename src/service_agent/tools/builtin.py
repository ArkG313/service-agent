"""
内置工具集 —— 客服场景常用工具。
"""

from __future__ import annotations

import datetime
from typing import Any

from service_agent.tools.base import BaseTool


class GetTimeTool(BaseTool):
    """获取当前时间。"""

    @property
    def name(self) -> str:
        return "get_current_time"

    @property
    def description(self) -> str:
        return "获取当前的日期和时间。当用户询问时间、日期时使用。"

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "description": "时区,默认 Asia/Shanghai"},
            },
        }

    def execute(self, timezone: str = "Asia/Shanghai", **kwargs: Any) -> str:
        now = datetime.datetime.now()
        return f"当前时间({timezone}): {now.strftime('%Y-%m-%d %H:%M:%S')}"


class QueryOrderTool(BaseTool):
    """查询订单状态。"""

    @property
    def name(self) -> str:
        return "query_order_status"

    @property
    def description(self) -> str:
        return "根据订单号查询订单状态。当用户询问订单进度、物流状态时使用。"

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "订单编号,如 ORD-2024-001"},
            },
            "required": ["order_id"],
        }

    def execute(self, order_id: str, **kwargs: Any) -> str:
        # TODO: 对接真实订单系统
        mock = {
            "ORD-2024-001": "已发货,预计明天送达",
            "ORD-2024-002": "正在打包,预计今天发出",
            "ORD-2024-003": "已完成签收",
        }
        status = mock.get(order_id)
        if status:
            return f"订单 {order_id} 状态: {status}"
        return f"未找到订单 {order_id},请确认订单号。"


class EscalateToHumanTool(BaseTool):
    """转人工客服。"""

    @property
    def name(self) -> str:
        return "escalate_to_human"

    @property
    def description(self) -> str:
        return "将对话转接给人工客服。当问题超出范围或用户要求人工服务时使用。"

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "description": "转人工原因"},
            },
            "required": ["reason"],
        }

    def execute(self, reason: str, **kwargs: Any) -> str:
        ticket = f"TKT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        return f"已创建转人工工单 {ticket}。原因: {reason}。客服将在5分钟内联系您。"


class CalculateShippingFeeTool(BaseTool):
    """运费计算。"""

    @property
    def name(self) -> str:
        return "calculate_shipping_fee"

    @property
    def description(self) -> str:
        return "根据目的地省份和重量计算运费。"

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "province": {"type": "string", "description": "目的省份"},
                "weight_kg": {"type": "number", "description": "包裹重量(kg)"},
            },
            "required": ["province", "weight_kg"],
        }

    def execute(self, province: str, weight_kg: float, **kwargs: Any) -> str:
        remote = {"新疆", "西藏", "青海", "内蒙古", "宁夏"}
        base = 15.0 if province in remote else 8.0
        per_kg = 8.0 if province in remote else 3.0
        fee = base + per_kg * max(weight_kg, 0.1)
        return f"寄往 {province},{weight_kg}kg 运费约 ¥{fee:.1f}"


def get_default_tools() -> list[BaseTool]:
    """获取默认工具集。"""
    return [
        GetTimeTool(),
        QueryOrderTool(),
        EscalateToHumanTool(),
        CalculateShippingFeeTool(),
    ]
