from dotenv import load_dotenv
from abc import ABC, abstractmethod  # abc：抽象基类模块，用来定义"必须被子类实现的方法"
from typing import Optional  # Optional：表示返回值可能为None
# Embeddings 是 LangChain 里所有嵌入模型的基类（把文字转成向量的接口）
from langchain_core.embeddings import Embeddings
# BaseChatModel 是 LangChain 里所有聊天模型的基类
from langchain_core.language_models.chat_models import BaseChatModel
# DashScopeEmbeddings：阿里云百炼平台的嵌入模型（把文字转成向量）
from langchain_community.embeddings import DashScopeEmbeddings
# ChatOpenAI：OpenAI兼容的聊天模型，可以配置成用智谱的模型
from langchain_openai import ChatOpenAI
# 导入RAG配置，里面包含嵌入模型的名称
from utils.config_handler import rag_conf

load_dotenv()

class BaseModelFactory(ABC):
    """模型工厂的抽象类，所有具体的工厂子类都必须实现generator方法"""
    @abstractmethod
    def generator(self)->Optional[Embeddings|BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):
    def generator(self)->Optional[Embeddings|BaseChatModel]:
        return ChatOpenAI(
            model=rag_conf["chat_model_name"],
            base_url="https://open.bigmodel.cn/api/paas/v4/",
        )
    
class EmbeddingsFactory(BaseModelFactory):
    def generator(self)->Optional[Embeddings|BaseChatModel]:
        return DashScopeEmbeddings(model=rag_conf["embedding_model_name"])
    

chat_model=ChatModelFactory().generator()

embed_model=EmbeddingsFactory().generator()


if __name__=='__main__':
    print(chat_model.invoke("你好").content)