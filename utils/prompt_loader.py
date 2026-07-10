"""
提示词加载模块。

为什么需要这个文件？
- 提示词（Prompt）是指导大模型如何回答的"指令文本"
- 提示词很长，写在代码里不方便修改和调试
- 把提示词放在 prompts/ 文件夹下的 txt 文件中，代码负责读取
- 路径配置放在 config/prompts.yml，实现配置与代码分离

这个文件有3个加载函数，分别加载3种提示词：
- system_prompt：Agent 的默认人设和行为指南
- rag_prompt：RAG 总结指令（根据检索到的参考资料总结回答）
- report_prompt：报告生成指令（让模型生成使用报告）
"""
from utils.config_handler import prompts_conf
from utils.path_tool import get_abs_path
from utils.logger_handler import logger


def load_system_prompts():
    """
    加载系统主提示词（Agent 的默认人设和行为指南）。

    流程：
    1. 从 prompts_conf（prompts.yml 的字典）取出路径
    2. 转为绝对路径
    3. 读取文件内容并返回

    双重 try-except 设计：
    - 第一层 except KeyError：配置项缺失（yaml 里没写这个键）
    - 第二层 except Exception：文件读取失败（文件不存在、权限不足等）
    """
    try:
        system_prompt_path = get_abs_path(prompts_conf["main_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_system_prompts]在yaml配置项中没有main_prompt_path配置项")
        raise e
    try:
        return open(system_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_system_prompts]解析系统提示词出错，{str(e)}")
        raise e


def load_rag_prompts():
    """加载 RAG 总结提示词（让模型根据检索到的参考资料总结回答的指令）"""
    try:
        rag_prompt_path = get_abs_path(prompts_conf["rag_summarize_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_rag_prompts]在yaml配置项中没有rag_summarize_prompt_path配置项")
        raise e

    try:
        return open(rag_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_rag_prompts]解析RAG提示词出错，{str(e)}")
        raise e


def load_report_prompts():
    """
    加载报告生成提示词（让模型生成使用报告的专用指令）。

    当中间件检测到用户要求生成报告时，会切换到这个提示词。
    """
    try:
        # 从配置里取出报告提示词文件的路径
        report_prompt_path = get_abs_path(prompts_conf["report_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_report_prompts]在yaml配置项中没有report_prompt_path配置项")
        raise e

    try:
        return open(report_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_report_prompts]解析报告生成提示词出错，{str(e)}")
        raise e


if __name__ == "__main__":
    print(load_report_prompts())