import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # ファイルハンドラ（ログローテーション付き）
    fh = RotatingFileHandler("trading_bot.log", maxBytes=50*1024*1024, backupCount=10)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


def get_logger(name):
    return logging.getLogger(name)