"""
Agent 工具集模块。

什么是工具（Tool）？
- 在 ReAct Agent 架构中，模型本身只会"思考和说话"，不能查数据库、调API
- "工具"就是给模型扩展的能力，比如：查天气、查知识库、查用户数据
- 模型在推理过程中可以自主决定"要不要调用某个工具"

为什么需要这个文件？
- 这里定义了 Agent 可以使用的所有工具（共7个）
- 每个工具用 @tool 装饰器注册，description 非常重要——模型根据描述决定用不用这个工具
- 工具分为三类：
  1. 知识检索：rag_summarize（RAG 查知识库）
  2. 模拟数据：get_weather / get_user_location / get_user_id / get_current_month / fetch_external_data
  3. 上下文触发：fill_context_for_report（触发报告生成模式）
"""
import os
from utils.logger_handler import logger  # 日志器
# @tool 是 LangChain 的装饰器，把普通函数变成"工具"，让 AI 模型可以自主调用
from langchain_core.tools import tool

from rag.rag_service import RagSummarizeService  # RAG 总结服务
import random  # 随机数模块，用来模拟数据
from utils.config_handler import agent_conf  # Agent 配置
from utils.path_tool import get_abs_path  # 路径工具

# 创建 RAG 服务实例（模块级单例，所有工具共享一个实例）
rag = RagSummarizeService()

# 模拟用户 ID 列表（实际项目里应该从数据库或登录信息获取）
user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010"]
# 2025年的12个月列表
month_arr = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06",
             "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12"]

# 外部数据缓存（从 CSV 读取后存在这里，避免每次调用都重新读文件）
external_data = {}


# ====== 工具1：RAG 知识检索 ======
# @tool 装饰器里的 description 非常重要：AI 模型会根据这个描述决定要不要调用这个工具
@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    """用用户的问题去知识库搜索相关资料，并让模型总结回答"""
    return rag.rag_summarize(query)


# ====== 工具2：获取天气 ======
@tool(description="获取指定城市的天气，以消息字符串的形式返回")
def get_weather(city: str) -> str:
    """模拟天气查询（实际项目应该调用真实天气API）"""
    return f"城市{city}天气为晴天，气温26摄氏度，空气湿度50%，南风1级，AQI21，最近6小时降雨概率极低"


# ====== 工具3：获取用户位置 ======
@tool(description="获取用户所在城市的名称，以纯字符串形式返回")
def get_user_location() -> str:
    """模拟获取用户位置（实际项目应该从GPS或IP获取）"""
    return random.choice(["深圳", "合肥", "杭州"])  # 随机返回一个城市


# ====== 工具4：获取用户ID ======
@tool(description="获取用户的ID，以纯字符串形式返回")
def get_user_id() -> str:
    """模拟获取当前用户ID"""
    return random.choice(user_ids)  # 从列表里随机选一个


# ====== 工具5：获取当前月份 ======
@tool(description="获取当前月份，以纯字符串形式返回")
def get_current_month() -> str:
    """模拟获取当前月份"""
    return random.choice()


# ====== 内部函数：从CSV读取外部数据到内存 ======
def generate_external_data():
    """
    从 CSV 文件读取数据，存入 external_data 字典。

    数据结构如下：
    {
        "1001": {                              # 用户ID
            "2025-01" : {"特征": xxx, "效率": xxx, ...},  # 某月的数据
            "2025-02" : {"特征": xxx, "效率": xxx, ...},
            ...
        },
        "1002": {
            "2025-01" : {"特征": xxx, "效率": xxx, ...},
            ...
        },
        ...
    }

    为什么用字典缓存？
    - CSV 文件不大但每次调用工具都读一遍 IO 开销大
    - 读一次存内存里（external_data），后续查询走内存，速度快很多

    :return: None
    """
    # 如果 external_data 已经有数据了，就不重复读取
    if not external_data:
        # 从配置里获取外部数据文件的路径
        external_data_path = get_abs_path(agent_conf["external_data_path"])

        # 检查文件是否存在
        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部数据文件{external_data_path}不存在")

        # 打开 CSV 文件读取
        with open(external_data_path, "r", encoding="utf-8") as f:
            # readlines()[1:] 跳过第一行（表头），从第二行开始读
            for line in f.readlines()[1:]:
                # strip() 去掉首尾空白，split(",") 按逗号分割成列表
                arr: list[str] = line.strip().split(",")

                # CSV 每行有6列：用户ID, 特征, 效率, 耗材, 对比, 时间
                # replace('"', '') 去掉字段两端的引号
                user_id: str = arr[0].replace('"', "")
                feature: str = arr[1].replace('"', "")
                efficiency: str = arr[2].replace('"', "")
                consumables: str = arr[3].replace('"', "")
                comparison: str = arr[4].replace('"', "")
                time: str = arr[5].replace('"', "")

                # 如果这个用户还没在字典里，先创建一个空字典
                if user_id not in external_data:
                    external_data[user_id] = {}

                # 按用户ID -> 月份 -> 数据的结构存储
                external_data[user_id][time] = {
                    "特征": feature,
                    "效率": efficiency,
                    "耗材": consumables,
                    "对比": comparison,
                }


# ====== 工具6：获取外部数据 ======
@tool(description="从外部系统中获取指定用户在指定月份的使用记录，以纯字符串形式返回， 如果未检索到返回空字符串")
def fetch_external_data(user_id: str, month: str) -> str:
    """查询指定用户在某个月的使用记录"""
    # 先确保数据已加载到内存
    generate_external_data()

    try:
        # 从字典中取数据：用户ID -> 月份 -> 数据
        return external_data[user_id][month]
    except KeyError:
        # 如果用户ID或月份不存在，返回空字符串
        logger.warning(f"[fetch_external_data]未能检索到用户：{user_id}在{month}的使用记录数据")
        return ""


# ====== 工具7：触发报告生成 ======
@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息")
def fill_context_for_report():
    """
    这个工具本身不做什么实际操作，但它是一个"信号触发器"。

    工作原理：
    - 中间件（middleware.py 的 monitor_tool）会监控所有工具调用
    - 当检测到 fill_context_for_report 被调用时，设置 context["report"] = True
    - 另一个中间件（report_prompt_switch）检测到 report=True 后，切换到报告生成提示词
    - 这样就实现了"动态切换提示词"的功能
    """
    return "fill_context_for_report已调用"


if __name__ == '__main__':
    print(rag_summarize.invoke({"query": "扫地机器人"}))
    print(get_weather.invoke({"city": "合肥"}))