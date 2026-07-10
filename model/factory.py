"""
模型工厂模块。

为什么需要这个文件？
- 项目用到两种模型：聊天模型（用于对话）和嵌入模型（把文字转成向量）
- 用工厂模式（Factory Pattern）来创建模型，好处是：
  1. 创建逻辑集中在一处，方便统一管理和维护
  2. 如果将来换模型（比如从智谱换成文心一言），只改工厂类就行，不用到处改代码
  3. 屏蔽了不同模型初始化参数的差异

- 聊天模型：智谱 GLM-4-flash（通过 ChatOpenAI 配置 base_url 指向智谱）
- 嵌入模型：阿里 DashScope text-embedding-v4（把文字转成高维向量）
"""
from dotenv import load_dotenv  # 从 .env 文件加载环境变量（如 API Key）
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
# 导入 RAG 配置，里面包含模型名称
from utils.config_handler import rag_conf

# 从 .env 文件加载环境变量（API_KEY 等敏感信息不写死在代码里）
load_dotenv()


class BaseModelFactory(ABC):
    """
    模型工厂的抽象基类（ABC）。

    为什么用抽象基类？
    - 定义一个"模板"，规定所有子类必须实现 generator() 方法
    - 如果子类不实现，Python 会在实例化时报错，防止遗漏
    - 实现了"面向接口编程"，调用方不需要知道具体是哪个工厂
    """
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        """子类必须实现：返回一个模型实例"""
        pass


class ChatModelFactory(BaseModelFactory):
    """聊天模型工厂：创建智谱 GLM 聊天模型实例"""
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        # ChatOpenAI 虽然名字带 OpenAI，但通过 base_url 指向智谱的 API 地址
        # 就可以调用智谱的 GLM 模型了（智谱兼容了 OpenAI 的接口格式）
        # API Key 会自动从环境变量 DASHSCOPE_API_KEY / OPENAI_API_KEY 读取
        return ChatOpenAI(
            model=rag_conf["chat_model_name"],  # 模型名从配置文件读
            base_url="https://open.bigmodel.cn/api/paas/v4/",  # 智谱 API 地址
        )


class EmbeddingsFactory(BaseModelFactory):
    """嵌入模型工厂：创建阿里 DashScope 嵌入模型实例"""
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        # 嵌入模型的作用：把文本转成一组数字（向量），用于相似度搜索
        # DashScope 的 API Key 从环境变量 DASHSCOPE_API_KEY 读取
        return DashScopeEmbeddings(model=rag_conf["embedding_model_name"])


# ====== 模块级实例：import 时就创建好模型，其他文件直接用 ======
chat_model = ChatModelFactory().generator()   # 聊天模型实例
embed_model = EmbeddingsFactory().generator()  # 嵌入模型实例


if __name__ == '__main__':
    # 直接运行本文件时，测试聊天模型是否能正常调用
    print(chat_model.invoke("你好").content)