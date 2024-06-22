import logging

# 创建logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)  # 设置最低日志级别

# 创建控制台handler并设置级别为DEBUG
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

# 创建文件handler并设置级别为WARNING
file_handler = logging.FileHandler('logfile.log',mode = 'w')
file_handler.setLevel(logging.DEBUG)

# 创建formatter并添加到handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 将handlers添加到logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 记录日志消息
mytest=1123445
logger.debug(f'This is a debug message{mytest}')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical message')




print('Hello word')
print('I am testing the stability of the sever')
print('Now we can start the BIT Hello word')