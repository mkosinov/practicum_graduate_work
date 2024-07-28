import logging.handlers
from functools import lru_cache
from logging import Logger as PyLogger

from core.settings import get_settings


class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        if get_settings().debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(get_settings().logger.logging_level)
        formatter = logging.Formatter(
            "[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        file_handler = logging.handlers.RotatingFileHandler(
            get_settings().logger.logs_dir.joinpath(f"{name}.log"),
            mode="a",
            maxBytes=get_settings().logger.max_bytes,
            backupCount=get_settings().logger.backup_count,
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        console_handler = logging.StreamHandler()
        self.logger.addHandler(console_handler)


@lru_cache(maxsize=1)
def get_logger() -> PyLogger:
    return Logger("assistant").logger
