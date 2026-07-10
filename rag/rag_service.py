"""
RAG 总结服务模块。

什么是 RAG？
- RAG = Retrieval-Augmented Generation（检索增强生成）
- 大模型本身不一定知道你们公司的私有知识（如扫地机器人手册）
- RAG 的思路：先从知识库检索相关资料，再把资料和问题一起交给模型，让它"看着资料"回答
- 这样模型回答更准确，不会"胡说八道"（减少幻觉）

这个模块做了什么？
- 接收用户的问题 → 从向量库检索相关文档 → 拼接成参考资料 → 交给模型总结回复
- 使用 LangChain 的 LCEL（LangChain Expression Language）链式语法来组装流程
"""
from langchain_core.documents import Document  # LangChain 文档类型
from langchain_core.output_parsers import StrOutputParser  # 字符串输出解析器，把模型返回的结果转成纯字符串

from rag.vector_store import VectorStoreService  # 向量存储服务
from utils.prompt_loader import load_rag_prompts  # 加载 RAG 提示词
from langchain_core.prompts import PromptTemplate  # 提示词模板，可以填入变量
from model.factory import chat_model  # 聊天模型


class RagSummarizeService:
    """
    RAG 总结服务：检索知识 + 模型总结回复。

    这是整个 RAG 模块对外的统一入口，其他文件只需创建这个类的实例，
    调用 rag_summarize(query) 就能得到基于知识库的回答。
    """

    def __init__(self):
        # 组装 RAG 所需的所有组件：
        # 向量存储服务（负责检索）→ 检索器 → 提示词模板 → 模型 → LCEL 链
        self.vector_store = VectorStoreService()       # 向量存储服务实例
        self.retriever = self.vector_store.get_retriever()  # 从向量库获取检索器
        self.prompt_text = load_rag_prompts()           # 加载 RAG 总结提示词文本
        # PromptTemplate.from_template 把含 {变量} 的文本转成可填充的模板
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model                         # 聊天模型（智谱 GLM）
        self.chain = self._init_chain()                # 初始化 LCEL 链

    def _init_chain(self):
        """
        初始化 LCEL 链（LangChain Expression Language）。

        LCEL 链就像一条流水线：提示词模板 → 模型 → 输出解析器
        用 | 管道符连接，前一步的输出自动作为后一步的输入。

        - PromptTemplate：填入变量（用户问题、参考资料），生成完整提示词
        - ChatModel：接收提示词，调用大模型，返回 AI 消息对象
        - StrOutputParser：把 AI 消息对象解析成纯字符串（方便直接使用）
        """
        return self.prompt_template | self.model | StrOutputParser()

    def retriever_docs(self, query: str) -> list[Document]:
        """用用户的提问去知识库检索相关文档"""
        return self.retriever.invoke(query)

    def rag_summarize(self, query: str) -> str:
        """
        完整的 RAG 流程：检索知识 + 模型总结。

        流程三步：
        1. retriever_docs(query)：用用户问题检索最相关的3段文档
        2. 把检索到的文档拼接成一段文本（参考资料）
        3. chain.invoke()：把用户问题和参考资料填入提示词模板，交给模型总结

        :param query: 用户的问题
        :return: 模型生成的回答文本
        """
        # 第一步：用用户的问题去知识库搜索相关内容
        context_docs = self.retriever_docs(query)

        # 第二步：把搜索到的文档拼成一段文本，作为给模型的参考资料
        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            # page_content 是文档的文本内容，metadata 是元数据（如来源、页码等）
            context += f"【参考资料{counter}】: 参考资料：{doc.page_content} | 参考元数据：{doc.metadata}\n"

        # 第三步：把用户问题和参考资料一起交给模型，让模型总结回答
        # chain.invoke() 会执行整条链：填入变量 → 调用模型 → 解析输出
        return self.chain.invoke(
            {
                "input": query,      # 用户的问题
                "context": context   # 检索到的参考资料
            }
        )


# ====== 下面是测试代码 ======
if __name__ == '__main__':
    # 创建 RAG 服务
    rag = RagSummarizeService()

    # 测试：问一个问题，看看 RAG 怎么回答
    print(rag.rag_summarize("小户型适合哪些扫地机器人"))