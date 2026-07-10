"""
文件处理工具集。

为什么需要这个文件？
- 知识库需要从 data/ 文件夹读取各种格式的文件（txt、pdf），并转为 LangChain 的 Document 对象
- 需要判断哪些文件已经处理过（用 MD5 去重），避免重复向量化
- 这些文件操作逻辑抽取出来，方便复用
"""
import os
import hashlib  # 提供 MD5 等哈希算法
from utils.logger_handler import logger
from utils.path_tool import get_abs_path
from langchain_core.documents import Document  # LangChain 的标准文档类型
from langchain_community.document_loaders import PyPDFLoader, TextLoader  # LangChain 的文档加载器


def get_file_md5_hex(filepath: str):
    """
    计算文件的 MD5 哈希值（文件的"指纹"）。

    为什么用 MD5？
    - 文件内容一样，MD5 就一样；内容哪怕改了一个字，MD5 完全不同
    - 用于知识库去重：已处理过的文件不需要重复向量化

    为什么分块读取？
    - 大文件（几百MB的PDF）一次性读进内存会撑爆
    - 用 chunk_size=4096 分块读取，每次只读 4KB

    :param filepath: 文件路径
    :return: MD5 哈希字符串，出错返回 None
    """
    if not os.path.exists(filepath):
        logger.error(f"[MD5计算]路径{filepath}不是文件")
        return
    if not os.path.isfile(filepath):
        logger.error(f"[MD5]计算路径{filepath}不是文件")
        return

    md5_obj = hashlib.md5()  # 创建 MD5 计算对象
    chunk_size = 4096  # 每次读取 4KB
    try:
        with open(filepath, "rb") as f:  # "rb" 表示二进制只读模式
            # 海象运算符 :=  同时赋值和判断，读到空（文件结束）就停止
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)  # 把这块数据"喂"给 MD5 计算器

        md5_hex = md5_obj.hexdigest()  # 获取最终的 MD5 字符串
        return md5_hex
    except Exception as e:
        logger.error(f"计算文件{filepath}md5失败，{str(e)}")
        return None


def listdir_with_allowed_type(path: str, allowed_types: tuple[str]):
    """
    列出文件夹内所有指定类型的文件。

    :param path: 文件夹路径
    :param allowed_types: 允许的文件后缀元组，如 ("txt", "pdf")
    :return: 匹配文件的完整路径元组
    """
    files = []
    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type]{path}不是文件夹")
        return allowed_types

    for f in os.listdir(path):
        if f.endswith(allowed_types):  # endswith 支持传入元组，一次匹配多种后缀
            files.append(os.path.join(path, f))
    return tuple(files)


def pdf_loader(filepath: str, passwd=None) -> list[Document]:
    """读取PDF文件，返回 Document 列表（passwd 用于加密PDF）"""
    return PyPDFLoader(filepath, passwd).load()


def txt_loader(filepath: str) -> list[Document]:
    """读取TXT文件，返回 Document 列表"""
    return TextLoader(filepath, encoding="utf-8").load()


if __name__ == '__main__':
    md5 = get_file_md5_hex(get_abs_path("data/选购指南.txt"))
    print(f"MD5:{md5}")