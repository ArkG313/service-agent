from langchain.agents import create_agent  # create_agent：创建 ReAct 智能体
from model.factory import chat_model  # 聊天模型
from utils.prompt_loader import load_system_prompts  # 加载系统提示词
# 导入所有工具（这些是AI可以自主调用的函数）
from agent.tools.agent_tools import (rag_summarize, get_weather, get_user_location, get_user_id,
                                     get_current_month, fetch_external_data, fill_context_for_report)
# 导入所有中间件（在工具执行和模型调用时自动插入的逻辑）
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch


class ReactAgent:
    """ReAct 智能体：Reasoning + Acting，让AI边思考边行动"""

    def __init__(self):
        # create_agent 创建一个完整的 ReAct Agent
        # ReAct 的工作循环：思考(Reasoning) -> 行动(Acting/调用工具) -> 观察(Observing结果) -> 再思考...
        self.agent = create_agent(
            model=chat_model,           # AI 聊天模型
            system_prompt=load_system_prompts(),  # 系统提示词（定义AI的人设和行为规范）
            tools=[rag_summarize, get_weather, get_user_location, get_user_id,
                   get_current_month, fetch_external_data, fill_context_for_report],  # 可用的工具列表
            middleware=[monitor_tool, log_before_model, report_prompt_switch],  # 中间件列表
        )

    def execute_stream(self, query: str):
        """流式执行：逐段返回AI的回复，不用等全部生成完才显示"""
        # 构造输入：用户的问题作为一条 user 消息
        input_dict = {
            "messages": [
                {"role": "user", "content": query},  # role=user 表示这是用户说的话
            ]
        }

        # stream() 流式输出，每次产出一段结果
        # stream_mode="values" 表示每次返回完整的状态快照
        # context={"report": False} 设置运行时上下文，report=False 表示初始不是报告模式
        # 这个 context 就是中间件里用来切换提示词的标记
        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            # 取最新的一条消息
            latest_message = chunk["messages"][-1]
            # 如果消息有内容，就 yield（产出）出去
            if latest_message.content:
                # strip() 去首尾空白，加换行
                yield latest_message.content.strip() + "\n"


# ====== 下面是测试代码 ======
if __name__ == '__main__':
    # 创建 Agent 实例
    agent = ReactAgent()

    # 流式执行一个问题，逐段打印
    for chunk in agent.execute_stream("给我生成我的使用报告"):
        # end="" 不换行（因为chunk里已经有换行），flush=True 立即输出不等缓存
        print(chunk, end="", flush=True)
