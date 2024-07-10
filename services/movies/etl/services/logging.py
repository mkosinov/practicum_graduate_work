"""Логгирование проекта."""

import logging
from logging.handlers import RotatingFileHandler

from settings import COUNT_LOG_FILES, LOG_FILE_NAME, LOG_FILE_SIZE, LOG_FORMAT


def setup_logging():
    """Настройка логгирования."""
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            # Ротация лог-файлов.
            RotatingFileHandler(
                LOG_FILE_NAME,
                maxBytes=LOG_FILE_SIZE,
                backupCount=COUNT_LOG_FILES,
            ),
            logging.StreamHandler(),
        ],
    )
