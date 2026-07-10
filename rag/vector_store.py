"""
向量存储服务模块。

为什么需要这个文件？
- RAG（检索增强生成）需要先把知识文档存到向量库，查询时再检索出来
- 这个模块负责：把知识文件→分片→嵌入→存入 Chroma 向量库，并提供检索功能
- 同时用 MD5 做文件级去重，避免每次启动都重复加载同一个文件

核心概念：
- 向量库：把文字转成数字向量后存储，可以按"语义相似度"搜索（而不仅是关键字匹配）
- 分片（Split）：把长文章切成小段，每段单独向量化，检索时更精确
- 嵌入（Embedding）：把文字转成向量的过程，由嵌入模型完成
"""
from langchain_chroma import Chroma  # Chroma 是一个向量数据库，用来存储和检索文本向量
from langchain_core.documents import Document  # Document 是 LangChain 的文档类型
from utils.config_handler import chroma_conf  # 导入 Chroma 配置

from model.factory import embed_model  # 导入嵌入模型（把文字转成向量的工具）

from langchain_text_splitters import RecursiveCharacterTextSplitter  # 文本分片器，把长文章切成小段
from utils.path_tool import get_abs_path  # 路径工具
from utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type, get_file_md5_hex  # 文件处理工具
from utils.logger_handler import logger  # 日志器
import os


class VectorStoreService:
    """
    向量存储服务：负责把知识文件存入向量库，以及提供检索功能。

    两个核心能力：
    1. load_document()：把 data/ 文件夹下的知识文件加载到向量库
    2. get_retriever()：返回一个检索器，根据查询词找到最相关的几段文本
    """

    def __init__(self):
        # 创建 Chroma 向量数据库实例
        # collection_name：集合名（类似数据库的表名）
        # embedding_function：嵌入函数（用哪个模型把文字转成向量）
        # persist_directory：数据存储到哪个文件夹
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=chroma_conf["persist_directory"],
        )

        # 创建文本分片器：把长文章切成一小段一小段的，方便检索
        # RecursiveCharacterTextSplitter 会递归地用分隔符来切分
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],        # 每个分片的最大长度（字符数）
            chunk_overlap=chroma_conf["chunk_overlap"],  # 分片之间的重叠量（避免切断了关键信息）
            separators=chroma_conf["separators"],        # 分隔符列表，优先用前面的分隔符切
            length_function=len,  # 用 len 函数计算长度（按字符数）
        )

    def get_retriever(self):
        """
        获取检索器：传入一个问题，返回最相关的几段文本。

        k=3 表示每次返回相似度最高的3段文本。
        """
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})

    def load_document(self):
        """
        从数据文件夹内读取数据文件，转为向量存入向量库。

        流程：
        1. 列出 data/ 文件夹下所有允许格式的文件（.txt .pdf）
        2. 对每个文件计算 MD5（文件的"指纹"）
        3. 检查 MD5 是否已记录过（去重），已处理过的跳过
        4. 读取文件内容 → 分片 → 存入向量库
        5. 记录 MD5，下次不再重复处理

        :return: None
        """

        def check_md5_hex(md5_for_check: str):
            """
            检查某个 MD5 是否已经记录过（即这个文件是否已加载过）。

            :param md5_for_check: 要检查的 MD5 值
            :return: True 表示已存在（已加载过），False 表示不存在
            """
            # 如果 MD5 记录文件不存在，先创建一个空文件
            if not os.path.exists(get_abs_path(chroma_conf["md5_hex_store"])):
                open(get_abs_path(chroma_conf["md5_hex_store"]), "w", encoding="utf-8").close()
                return False
            # 打开 MD5 记录文件，逐行检查
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()  # 去掉首尾空白字符（含换行符）
                    if line == md5_for_check:
                        return True  # 找到了，说明已加载过

                return False  # 遍历完都没找到

        def save_md5_hex(md5_for_check: str):
            """把新的 MD5 追加写入记录文件"""
            # "a" 表示追加模式，在文件末尾添加，不会覆盖原有内容
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")  # 写入 MD5 并换行

        def get_file_documents(read_path: str):
            """根据文件后缀选择对应的加载器，返回 Document 列表"""
            if read_path.endswith("txt"):
                return txt_loader(read_path)  # 用 TXT 加载器读取

            if read_path.endswith("pdf"):
                return pdf_loader(read_path)  # 用 PDF 加载器读取

            return []  # 不支持的格式返回空列表

        # 先列出数据文件夹里所有允许格式的文件（.txt .pdf等）
        allowed_files_path: list[str] = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),
            tuple(chroma_conf["allow_knowledge_file_type"]),
        )

        # 遍历每一个文件
        for path in allowed_files_path:
            # 获取这个文件的 MD5 哈希值（相当于文件的"指纹"，内容一样 MD5 就一样）
            md5_hex = get_file_md5_hex(path)

            # 检查这个 MD5 是否已经处理过（去重）
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]{path}内容已经存在知识库内，跳过")
                continue  # 跳过这个文件，不重复加载

            try:
                # 读取文件内容，得到 Document 列表
                documents: list[Document] = get_file_documents(path)

                # 如果文件没有有效内容，跳过
                if not documents:
                    logger.warning(f"[加载知识库]{path}内没有有效文本内容，跳过")
                    continue

                # 把长文档切成小段（分片），方便后续检索
                split_document: list[Document] = self.spliter.split_documents(documents)

                # 如果分片后没有内容，跳过
                if not split_document:
                    logger.warning(f"[加载知识库]{path}分片后没有有效文本内容，跳过")
                    continue

                # 将分片后的内容存入向量库
                # add_documents 会自动调用嵌入模型把文字转成向量再存储
                self.vector_store.add_documents(split_document)

                # 记录这个文件的 MD5，下次就不会重复加载了
                save_md5_hex(md5_hex)

                logger.info(f"[加载知识库]{path} 内容加载成功")
            except Exception as e:
                # exc_info=True 会记录详细的报错堆栈信息，方便调试
                logger.error(f"[加载知识库]{path}加载失败：{str(e)}", exc_info=True)
                continue  # 出错了就跳过这个文件，继续处理下一个


if __name__ == '__main__':
    # 创建向量存储服务
    vs = VectorStoreService()

    # 加载知识库文件到向量库
    vs.load_document()

    # 获取检索器
    retriever = vs.get_retriever()

    # 测试检索：用"迷路"作为查询词，看看能不能找到相关内容
    res = retriever.invoke("迷路")
    for r in res:
        print(r.page_content)    # 打印每段文本内容
        print("-" * 20)          # 打印分隔线