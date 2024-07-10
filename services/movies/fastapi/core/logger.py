from aiologger import Logger
from aiologger.formatters.base import StrFormatStyle
from aiologger.handlers.files import AsyncFileHandler
from aiologger.handlers.streams import AsyncStreamHandler
from aiologger.levels import LogLevel

LOG_FILE_NAME = "logs/fastapi.log"
LOG_FORMAT = "{asctime} - {name} - {levelname} - {message}"

# Создание и настройка логгера
logger = Logger.with_default_handlers(name=__name__)

# Установка уровня логгирования
logger.level = LogLevel.INFO

# Создание форматтера с собственным форматом
formatter = StrFormatStyle(fmt=LOG_FORMAT)

# Установка форматтера на логгер
logger.formatter = formatter

# Добавление обработчика для вывода в консоль
console_handler = AsyncStreamHandler()
logger.add_handler(console_handler)

# Добавление обработчика для записи в файл
file_handler = AsyncFileHandler(filename=LOG_FILE_NAME, mode="w")
file_handler.record_formatter = formatter
logger.add_handler(file_handler)
