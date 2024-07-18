# log_config.py
import logging

def setup_logging():
    # 创建logger
    logger = logging.getLogger('BTLOG')
    logger.setLevel(logging.INFO)  # 设置最低日志级别

    # 创建控制台handler并设置级别为DEBUG
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 创建文件handler并设置级别为WARNING
    file_handler = logging.FileHandler('./debug/BTLOG.log',mode='w') # mode='w' 'a'
    file_handler.setLevel(logging.DEBUG)
 
    # 创建formatter并添加到handlers
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 将handlers添加到logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logging()