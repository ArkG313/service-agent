"""
为整个工程提供统一的绝对路径工具。

为什么需要这个文件？
- 如果在代码里把路径写死（如 /Users/xxx/service-agent/config/rag.yml），
  换一台电脑或换一个部署位置就找不到了。
- 通过本工具可以根据项目所在位置自动算出正确的绝对路径，
  全项目其他文件统一调用 get_abs_path() 来拼接路径，保证路径永远正确。
"""
import os


def get_project_root() -> str:
    """
    获取工程所在的根目录。

    原理：本文件位于「项目根/utils/path_tool.py」，
    - os.path.abspath(__file__)  得到本文件的绝对路径
    - dirname 一次                得到 utils/ 目录
    - dirname 两次                得到项目根目录

    注意：__file__ 是 Python 内置变量，始终指向「当前这个文件本身」，
          不管哪个文件调用本函数，__file__ 不会变。

    :return: 项目根目录的绝对路径字符串
    """
    current_file = os.path.abspath(__file__)   # 当前文件（path_tool.py）的绝对路径
    current_dir = os.path.dirname(current_file)  # 去掉文件名，得到 utils/ 目录
    project_root = os.path.dirname(current_dir)  # 再去掉一层，得到项目根目录
    return project_root


def get_abs_path(relative_path: str) -> str:
    """
    传入一个相对路径（比如 "config/rag.yml"），返回一个完整的绝对路径。

    :param relative_path: 相对路径，例如 "config/rag.yml"
    :return: 绝对路径，例如 "/Users/xxx/service-agent/config/rag.yml"
    """
    project_root = get_project_root()
    return os.path.join(project_root, relative_path)


if __name__ == '__main__':
    # 直接运行本文件时，打印一个示例路径，验证是否正确
    print(get_abs_path("config/rag.yml"))