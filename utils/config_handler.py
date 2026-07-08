"""
这个模块的作用就是读取yml配置文件，转成python的字典，方便代码利用
"""
import yaml  #导入yaml库，用来解析yml配置文件
from utils.path_tool import get_abs_path

def load_rag_config(config_path:str=get_abs_path("config/rag.yml"),encoding="utf-8"):
    """加载RAG相关配置"""
    # open()打开文件，with语法会在用完后自动关闭文件
    with open(config_path,"r",encoding=encoding) as f:
        return yaml.load(f,Loader=yaml.FullLoader)


def load_chroma_config(config_path: str = get_abs_path("config/chroma.yml"), encoding: str = "utf-8"):
    """加载向量数据库（Chroma）相关配置"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_prompts_config(config_path: str = get_abs_path("config/prompts.yml"), encoding: str = "utf-8"):
    """加载提示词相关配置"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_agent_config(config_path: str = get_abs_path("config/agent.yml"), encoding: str = "utf-8"):
    """加载 Agent 智能体相关配置"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


rag_conf=load_rag_config()
chroma_conf=load_chroma_config()
agent_conf=load_agent_config()
prompts_conf=load_prompts_config()

if __name__=='__main__':
    print(rag_conf["chat_model_name"])