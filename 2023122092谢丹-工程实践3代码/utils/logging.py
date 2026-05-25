# utils/logging.py
import logging
import config

def setup_logging():
    """配置日志系统"""
    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(config.LOG_FILE)
    file_handler.setLevel(config.LOG_LEVEL)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL)
    
    # 创建格式化器并添加到处理器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger