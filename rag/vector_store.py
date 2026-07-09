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
    """向量存储服务：负责把知识文件存入向量库，以及提供检索功能"""

    def __init__(self):
        # 创建Chroma向量数据库实例
        self.vector_store=Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=chroma_conf["persist_directory"],
        )

        # 创建文本分片器：把长文章切成一小段一小段的，方便检索
        self.spliter=RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],        # 每个分片的最大长度（字符数）
            chunk_overlap=chroma_conf["chunk_overlap"],  # 分片之间的重叠量（避免切断了关键信息）
            separators=chroma_conf["separators"],        # 分隔符列表，优先用前面的分隔符切
            length_function=len,  
        )

    def get_retriever(self):
        """获取检索器：传入一个问题，返回最相关的几段文本"""
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})
    
    def load_document(self):
        """
        从数据文件夹内读取数据文件，转为向量存入向量库
        要计算文件的MD5做去重（避免重复加载同一个文件）
        :return: None
        """
        def check_md5_hex(md5_for_check:str):
            if not os.path.exists(get_abs_path(chroma_conf["md5_hex_store"])):
                open(get_abs_path(chroma_conf["md5_hex_store"]), "w", encoding="utf-8").close()
                return False   
            # 打开MD5记录文件，逐行检查
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()  # 去掉首尾空白字符
                    if line == md5_for_check:
                        return True  
                    
                return False
            
        def save_md5_hex(md5_for_check: str):
            # "a" 表示追加模式，在文件末尾添加，不会覆盖原有内容
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")  # 写入MD5并换行

        def get_file_documents(read_path: str):
            if read_path.endswith("txt"):
                return txt_loader(read_path)  # 用TXT加载器读取

            if read_path.endswith("pdf"):
                return pdf_loader(read_path)  # 用PDF加载器读取

            return []  # 不支持的格式返回空列表
        
        # 先列出数据文件夹里所有允许格式的文件（.txt .pdf等）
        allowed_files_path: list[str] = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),
            tuple(chroma_conf["allow_knowledge_file_type"]),
        )
        # 遍历每一个文件
        for path in allowed_files_path:
            # 获取这个文件的MD5哈希值（相当于文件的"指纹"，内容一样MD5就一样）
            md5_hex = get_file_md5_hex(path)

             # 检查这个MD5是否已经处理过（去重）
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

                # 将分片后的内容存入向量库（嵌入模型会自动把文字转成向量存储）
                self.vector_store.add_documents(split_document)

                # 记录这个文件的MD5，下次就不会重复加载了
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
        print("-"*20)            # 打印分隔线