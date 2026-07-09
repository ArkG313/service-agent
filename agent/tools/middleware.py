from typing import Callable  # Callable：表示参数是一个可调用的函数
from utils.prompt_loader import load_system_prompts, load_report_prompts  # 加载提示词
# AgentState：Agent 的状态对象，保存了对话历史等信息
from langchain.agents import AgentState
# 中间件装饰器：
#   wrap_tool_call：包装工具调用（在工具执行前后插入逻辑）
#   before_model：在调用模型之前执行
#   dynamic_prompt：动态生成提示词
#   ModelRequest：模型请求的封装对象
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
# ToolCallRequest：工具调用请求的封装对象
from langchain.tools.tool_node import ToolCallRequest
# ToolMessage：工具返回的消息类型
from langchain_core.messages import ToolMessage
# Runtime：运行时上下文，保存了整个执行过程中的上下文信息
from langgraph.runtime import Runtime
# Command：LangGraph 的命令类型
from langgraph.types import Command
from utils.logger_handler import logger  # 日志器


# ====== 中间件1：工具执行监控 ======
# @wrap_tool_call 装饰器：这个函数会在每次工具被调用时自动执行
# 作用是记录日志，以及在特定工具被调用时设置标记
@wrap_tool_call
def monitor_tool(
        # request：包含工具调用信息的请求对象（工具名、参数等）
        request: ToolCallRequest,
        # handler：实际执行工具的函数，调用它就会执行工具
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:             # 返回工具执行结果
    # 记录日志：正在执行哪个工具
    logger.info(f"[tool monitor]执行工具：{request.tool_call['name']}")
    # 记录日志：传给工具的参数是什么
    logger.info(f"[tool monitor]传入参数：{request.tool_call['args']}")

    try:
        # 调用 handler 执行工具，拿到结果
        result = handler(request)
        logger.info(f"[tool monitor]工具{request.tool_call['name']}调用成功")

        # 特殊处理：如果调用的工具是 fill_context_for_report
        # 就在运行时上下文里标记 report=True，表示要切换到报告生成模式
        if request.tool_call['name'] == "fill_context_for_report":
            request.runtime.context["report"] = True

        return result
    except Exception as e:
        logger.error(f"工具{request.tool_call['name']}调用失败，原因：{str(e)}")
        raise e  # 重新抛出异常，不吞掉错误


# ====== 中间件2：模型调用前日志 ======
# @before_model 装饰器：这个函数会在每次调用AI模型之前自动执行
@before_model
def log_before_model(
        state: AgentState,          # Agent 的状态，包含对话历史 messages
        runtime: Runtime,           # 运行时上下文
):         # 在模型执行前输出日志
    # 记录日志：即将调用模型，当前有多少条消息
    logger.info(f"[log_before_model]即将调用模型，带有{len(state['messages'])}条消息。")

    # 记录调试日志：最后一条消息的类型和内容（debug级别，控制台不显示，文件里有）
    logger.debug(f"[log_before_model]{type(state['messages'][-1]).__name__} | {state['messages'][-1].content.strip()}")

    return None  # 返回None表示不修改任何东西，只是记录日志


# ====== 中间件3：动态提示词切换 ======
# @dynamic_prompt 装饰器：每次模型需要提示词时，会调用这个函数
# 作用是根据上下文决定用哪个提示词
@dynamic_prompt
# 每一次在生成提示词之前，调用此函数
def report_prompt_switch(request: ModelRequest):     # 动态切换提示词
    # 从运行时上下文里读取 report 标记，默认为 False
    is_report = request.runtime.context.get("report", False)
    if is_report:               # 是报告生成场景，返回报告生成提示词内容
        return load_report_prompts()

    # 不是报告场景，返回默认的系统提示词
    return load_system_prompts()
