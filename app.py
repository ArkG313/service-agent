"""
智扫通 · 智能客服 — Streamlit Web 应用入口。

为什么用 Streamlit？
- Streamlit 是一个专为机器学习/AI 应用设计的 Web 框架
- 不需要写 HTML/CSS/JS，纯 Python 就能搭出一个交互式网页
- 适合快速做原型和演示

这个文件做了什么？
- 初始化网页配置（标题、图标）
- 创建 ReAct Agent 实例（只创建一次，后续复用）
- 显示聊天界面（用户消息 + AI回复）
- 用流式输出实现"打字机"效果（逐字显示 AI 回复）
- 保存聊天记录到 session_state（刷新页面不丢失）
"""
from dotenv import load_dotenv  # 加载 .env 文件里的 API Key
load_dotenv()  # 读取 .env 文件，把里面的变量加到环境变量里

import streamlit as st  # Streamlit：快速搭建Web界面的库
from agent.react_agent import ReactAgent  # 导入 ReAct 智能体

# 设置网页标题和图标（必须在所有 Streamlit 命令之前调用）
st.set_page_config(page_title="智扫通 · 智能客服", page_icon="🤖")
# 页面主标题
st.title("🤖 智扫通机器人智能客服")
# 副标题（灰色小字）
st.caption("基于 LangChain ReAct Agent + RAG 检索增强")
# 分隔线
st.divider()

# session_state 是 Streamlit 的会话状态，页面刷新后数据不会丢
# 如果还没有创建 Agent，就创建一个（只创建一次，后续复用）
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

# 如果还没有聊天记录，就初始化一个空列表
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 遍历之前的聊天记录，重新显示在页面上（这样刷新页面后历史对话不会丢）
for message in st.session_state["messages"]:
    # chat_message() 创建聊天气泡，role 决定气泡在左边还是右边
    st.chat_message(message["role"]).write(message["content"])

# 显示聊天输入框，用户输入的文字会赋值给 prompt
prompt = st.chat_input()

# 如果用户输入了内容
if prompt:
    # 在页面上显示用户的消息（右侧气泡）
    st.chat_message("user").write(prompt)
    # 把用户消息保存到聊天记录里
    st.session_state["messages"].append({"role": "user", "content": prompt})

    # 用来缓存 AI 完整回复的列表（因为流式输出是一段一段的，需要拼接起来）
    response_messages: list[str] = []
    # 显示"思考中..."的加载动画
    with st.spinner("智能客服思考中..."):
        # 获取 Agent 的流式输出（一个生成器，每次 yield 一段文字）
        res_stream = st.session_state["agent"].execute_stream(prompt)

        # 定义一个生成器函数：逐字输出，同时把完整回复缓存起来
        def stream_generator(generator, cache_list):
            """
            逐字流式输出，同时缓存完整响应。

            为什么逐字？
            - Agent 的流式输出是一段一段的（可能一段好几个字）
            - 逐字 yield 可以实现更细腻的"打字机"效果
            - 同时把每一段存到 cache_list，最终拼成完整回复
            """
            for chunk in generator:        # 遍历生成器的每一段输出
                cache_list.append(chunk)   # 把这一段存到缓存列表
                for char in chunk:         # 把这一段拆成单个字符
                    yield char             # 逐个字符产出（实现打字机效果）

        # 在页面上显示 AI 的回复（左侧气泡），用流式方式逐字显示
        st.chat_message("assistant").write_stream(stream_generator(res_stream, response_messages))
        # 把完整的 AI 回复拼成字符串，保存到聊天记录
        st.session_state["messages"].append({"role": "assistant", "content": "".join(response_messages)})
        # st.rerun() 重新运行整个页面，把刚生成的 AI 回复也显示在历史记录里
        st.rerun()
