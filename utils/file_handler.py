import os,hashlib
from utils.logger_handler import logger
from utils.path_tool import get_abs_path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader,TextLoader

def get_file_md5_hex(filepath:str):
    if not os.path.exists(filepath):
        logger.error(f"[MD5计算]路径{filepath}不是文件")
        return
    if not os.path.isfile(filepath):
        logger.error(f"[MD5]计算路径{filepath}不是文件")
        return
    
    md5_obj=hashlib.md5()
    chunk_size=4096
    try:

            with open(filepath,"rb") as f:
                 while chunk:=f.read(chunk_size):
                      md5_obj.update(chunk)

            md5_hex=md5_obj.hexdigest()
            return md5_hex
    except Exception as e:
        logger.error(f"计算文件{filepath}md5失败，{str(e)}")          
        return None
    
def listdir_with_allowed_type(path:str,allowed_types:tuple[str]):
    files=[]
    if not os.path.isdir(path):
          logger.error(f"[lisdir_with_allowed_type]{path}不是文件夹")
          return allowed_types
     
    for f in os.listdir(path):
          if f.endswith(allowed_types):
               files.append(os.path.join(path,f))
    return tuple(files)

def pdf_loader(filepath:str,passwd=None)->list[Document]:
     """读取PDF文件，返回文档列表"""
     return PyPDFLoader(filepath,passwd).load()

def txt_loader(filepath:str)->list[Document]:
     """读取TXT文件，返回文档列表"""
     return TextLoader(filepath,encoding="utf-8").load()


if __name__=='__main__':
    md5=get_file_md5_hex(get_abs_path("data/选购指南.txt"))
    print(f"MD5:{md5}")