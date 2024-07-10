"""Дополнительные сервисы проекта."""

import logging
from functools import wraps
from time import sleep

from elasticsearch import ConnectionError, ConnectionTimeout
from psycopg2.errors import (
    ConnectionException,
    ConnectionFailure,
    InvalidTransactionState,
    OperationalError,
    SqlclientUnableToEstablishSqlconnection,
    TransactionResolutionUnknown,
)
from urllib3.exceptions import NewConnectionError

from services.logging import setup_logging

setup_logging()

logger = logging.getLogger(__name__)


def backoff(
    start_sleep_time=0.1,
    factor=2,
    border_sleep_time=10,
    max_attempts=5,
):
    """
    Функция для повторного выполнения функции через некоторое время,
    если возникла ошибка. Использует наивный экспоненциальный рост
    времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * (factor ^ n), если t < border_sleep_time
        t = border_sleep_time, иначе
    :param start_sleep_time: начальное время ожидания
    :param factor: во сколько раз нужно увеличивать время ожидания на каждой
    итерации
    :param border_sleep_time: максимальное время ожидания
    :param max_attempts: максимальное количество попыток
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            current_sleep_time = start_sleep_time
            attempts = 0

            while True:
                try:
                    result = func(*args, **kwargs)
                    return result
                except (
                    ConnectionError,
                    ConnectionException,
                    ConnectionFailure,
                    ConnectionTimeout,
                    InvalidTransactionState,
                    NewConnectionError,
                    OperationalError,
                    SqlclientUnableToEstablishSqlconnection,
                    TransactionResolutionUnknown,
                ) as error:
                    logger.error(f"Ошибка подключения к БД: {error}.")
                    sleep(current_sleep_time)

                    # Увеличиваем время ожидания на каждой итерации
                    current_sleep_time *= factor

                    # Если превышено максимальное время, используем его
                    if current_sleep_time > border_sleep_time:
                        current_sleep_time = border_sleep_time
                        attempts += 1

                        if attempts >= max_attempts:
                            raise RuntimeError(
                                f"Максимальное число попыток ({max_attempts}) достигнуто. Невозможно совершить операцию."
                            )

        return inner

    return func_wrapper
