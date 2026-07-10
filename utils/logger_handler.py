"""
日志处理模块。

为什么需要日志？
- 用 print() 输出的信息看一眼就没了，排查问题时找不到历史记录
- 日志（logging）可以同时输出到控制台和文件，方便排查问题
- 可以设置级别（DEBUG/INFO/WARNING/ERROR），灵活控制输出多少信息

这个文件做了什么？
- 创建一个名为 'agent' 的日志记录器
- 同时输出到控制台（INFO 级别，只看重要信息）和文件（DEBUG 级别，全量记录）
- 日志文件按天命名，如 agent_20250708.log
"""
import logging
from utils.path_tool import get_abs_path
import os
from datetime import time, datetime

# 日志保存的根目录（用 path_tool 算出项目根目录下的 logs 文件夹路径）
LOG_ROOT = get_abs_path("logs")

# 确保日志目录存在，exist_ok=True 表示如果文件夹已存在就不报错
os.makedirs(LOG_ROOT, exist_ok=True)

# 日志的格式配置
# 每条日志包含：时间 - 日志器名 - 级别 - 文件名:行号 - 消息内容
DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s-%(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)


def get_logger(
        name: str = "agent",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        log_file=None,
) -> logging.Logger:
    """
    创建并配置一个日志记录器（logger）。

    日志级别从低到高：DEBUG < INFO < WARNING < ERROR < CRITICAL
    - 整体设为 DEBUG：所有级别的日志都会被处理
    - 控制台设为 INFO：只显示 INFO 及以上（日常使用，不要太刷屏）
    - 文件设为 DEBUG：全量记录（排查问题时可以翻文件）

    :param name: 日志器名称（默认 "agent"）
    :param console_level: 控制台输出的最低日志级别
    :param file_level: 文件记录的最低日志级别
    :param log_file: 自定义日志文件路径，不传则自动按日期命名
    :return: 配置好的 logger 对象
    """
    # 创建一个日志器（logger）
    logger = logging.getLogger(name)
    # 设置整体日志级别为DEBUG（最低，什么都要）
    logger.setLevel(logging.DEBUG)

    # 避免重复添加 Handler，如果已经添加过了，就直接返回，不重复添加
    # （否则日志会被重复输出多遍）
    if logger.handlers:
        return logger

    # 第一个 Handler：输出到控制台（终端屏幕）
    console_handler = logging.StreamHandler()  # 创建控制台输出器
    console_handler.setLevel(console_level)   # 设置控制台日志级别
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)  # 给控制台日志套上格式

    logger.addHandler(console_handler)  # 把控制台输出器挂到日志器上

    # 第二个 Handler：输出到文件（存到硬盘上）
    # 如果没有指定日志文件路径，就自动生成一个
    if not log_file:
        # 文件名格式：agent_20250708.log（名字+当天日期）
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(file_handler)

    return logger


# 全局 logger 实例
# 其他模块只需要 `from utils.logger_handler import logger` 就能直接用
logger = get_logger()


if __name__ == '__main__':
    # 直接运行本文件时，测试各种级别的日志输出
    logger.info("信息日志")
    logger.error("错误日志")
    logger.warning("警告日志")
    logger.debug("调试日志")
