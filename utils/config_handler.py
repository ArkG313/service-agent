"""
这个模块的作用就是读取 yml 配置文件，转成 Python 的字典，方便代码利用。

为什么需要把配置放在 YAML 文件里？
- 如果把模型名、向量库路径等参数写死在代码里，每次修改都要改代码、重新部署。
- 把配置放在 YAML 文件里，修改配置不用动代码，运维和开发分离。
- YAML 格式比 JSON 更适合人读写（支持注释、缩进清晰）。
"""
import yaml  # 导入 yaml 库，用来解析 yml 配置文件
from utils.path_tool import get_abs_path


def load_rag_config(config_path: str = get_abs_path("config/rag.yml"), encoding="utf-8"):
    """加载 RAG 相关配置（模型名称等），返回字典"""
    # open() 打开文件，with 语法会在用完后自动关闭文件
    with open(config_path, "r", encoding=encoding) as f:
        # yaml.load 把 YAML 文本解析成 Python 字典
        # Loader=yaml.FullLoader 指定用完整加载器（安全，不执行任意代码）
        return yaml.load(f, Loader=yaml.FullLoader)


def load_chroma_config(config_path: str = get_abs_path("config/chroma.yml"), encoding: str = "utf-8"):
    """加载向量数据库（Chroma）相关配置（集合名、分片参数、检索数量等）"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_prompts_config(config_path: str = get_abs_path("config/prompts.yml"), encoding: str = "utf-8"):
    """加载提示词相关配置（各提示词文件的路径）"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_agent_config(config_path: str = get_abs_path("config/agent.yml"), encoding: str = "utf-8"):
    """加载 Agent 智能体相关配置（外部数据路径等）"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


# ====== 模块级变量：import 时就加载好配置，其他文件直接用 ======
rag_conf = load_rag_config()       # RAG 配置（模型名称）
chroma_conf = load_chroma_config()  # ChromaDB 配置（向量库参数）
agent_conf = load_agent_config()   # Agent 配置（外部数据路径）
prompts_conf = load_prompts_config()  # 提示词路径配置


if __name__ == '__main__':
    print(rag_conf["chat_model_name"])