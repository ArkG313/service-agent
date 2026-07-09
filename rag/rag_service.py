"""
总结服务类：用户提问，搜索参考资料，将提问和参考资料提交给模型，让模型总结回复
"""
from langchain_core.documents import Document  # LangChain 文档类型
from langchain_core.output_parsers import StrOutputParser  # 字符串输出解析器，把模型返回的结果转成纯字符串

from rag.vector_store import VectorStoreService  # 向量存储服务
from utils.prompt_loader import load_rag_prompts  # 加载RAG提示词
from langchain_core.prompts import PromptTemplate  # 提示词模板，可以填入变量
from model.factory import chat_model  # 聊天模型


class RagSummarizeService:
    """RAG总结服务：检索知识+模型总结回复"""
    def __init__(self):
        self.vector_store=VectorStoreService()
        self.retriever=self.vector_store.get_retriever()
        self.prompt_text=load_rag_prompts()
        self.prompt_template=PromptTemplate.from_template(self.prompt_text)
        self.model=chat_model
        self.chain=self._init_chain()

    def _init_chain(self):
        """初始化 LCEL 链（LangChain Expression Language）
        LCEL 链就像一条流水线：提示词模板 -> 模型 -> 输出解析器
        用 | 管道符连接，前一步的输出自动作为后一步的输入
        """
        return self.prompt_template|self.model|StrOutputParser()
    
    def retriever_docs(self,query:str)->list[Document]:
        """用用户的提问去知识库检索相关文档"""  
        return self.retriever.invoke(query)
    
    def rag_summarize(self,query:str)->str:
        """完整的RAG流程：检索知识+模型总结"""
        # 第一步：用用户的问题去知识库搜索相关内容
        context_docs=self.retriever_docs(query)
        # 第二步：把搜索到的文档拼成一段文本，作为给模型的参考资料
        context=""
        counter=0
        for doc in context_docs:
            counter+=1
            context+=f"【参考资料{counter}】: 参考资料：{doc.page_content} | 参考元数据：{doc.metadata}\n"

        # 第三步：把用户问题和参考资料一起交给模型，让模型总结回答
        # chain.invoke()会执行整条链：填入变量->调用模型->解析输出
        return self.chain.invoke(
            {
                "input":query,
                "context":context
            }
        )
    

    
# ====== 下面是测试代码 ======
if __name__ == '__main__':
    # 创建 RAG 服务
    rag = RagSummarizeService()

    # 测试：问一个问题，看看 RAG 怎么回答
    print(rag.rag_summarize("小户型适合哪些扫地机器人"))