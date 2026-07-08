import logging
from utils.path_tool import get_abs_path
import os
from datetime import time,datetime

# 日志保存的根目录（用path_tool算出项目根目录下的logs文件夹路径）
LOG_ROOT=get_abs_path("logs")

# 确保日志目录存在，exist_ok=True表示如果文件夹已存在就不报错
os.makedirs(LOG_ROOT,exist_ok=True)

# 日志的格式配置
# 每条日志包含：时间-日志器名-级别-文件名：行号-消息内容
DEFAULT_LOG_FORMAT=logging.Formatter(
    '%(asctime)s-%(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )

def get_logger(
        name:str="agent",
        console_level:int=logging.INFO,
        file_level:int=logging.DEBUG,
        log_file=None,
)->logging.Logger:
    # 创建一个日志器（logger）  
    logger=logging.getLogger(name)
    # 设置整体日志级别为DEBUG（最低，什么都要）
    logger.setLevel(logging.DEBUG)

    # 避免重复添加Handler，如果已经添加过了，就直接返回，不重复添加
    if logger.handlers:
        return logger
    
    # 第一个Handler：输出到控制台（终端屏幕）
    console_handler=logging.StreamHandler()  #创建控制台输出器
    console_handler.setLevel(console_level) # 设置控制台日志级别
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)    # 给控制台日志套上格式

    logger.addHandler(console_handler)       #把控制台输出器挂到日志器上

    # 第二个Handler：输出到文件（存到硬盘上）
    # 如果没有指定日志文件路径，就自动生成一个
    if not log_file:
        # 文件名格式：agent_20250708.log(名字+当天日期)
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(file_handler)

    return logger
    
logger=get_logger()

if __name__=='__main__':
    logger.info("信息日志")
    logger.error("错误日志")
    logger.warning("警告日志")
    logger.debug("调试日志")
