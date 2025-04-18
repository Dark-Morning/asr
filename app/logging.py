import logging

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 输出到控制台
    ]
)


def get_logger(name: str = None):
    if name is None:
        name = __name__
    return logging.getLogger(name)