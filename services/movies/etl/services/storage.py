"""Реализация хранилища сосояний."""
import json
import logging
import os
from json import JSONDecodeError
from typing import Any, Dict

from models import IndexName
from settings import START_SYNC_TIME, STATE_STORAGE_FILE

logger = logging.getLogger(__name__)


class JsonFileStorage:
    """Реализация хранилища, использующего локальный файл.
    Формат хранения: JSON
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        # Проверяем наличие файла состояний, создаем его, если отсутствует.
        if not os.path.exists(file_path):
            self.save_state({})

    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""
        with open(self.file_path, "w") as file:
            json.dump(state, file)

    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""
        json_object = {}
        try:
            with open(self.file_path, "r") as file:
                json_object = json.load(file)
        except JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}")
        except FileNotFoundError:
            logger.error(f"Файл состояния {self.file_path} не найден.")
        return json_object


class State:
    """Класс для работы с состояниями."""

    def __init__(self, storage: JsonFileStorage) -> None:
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа."""
        current_state = self.storage.retrieve_state()
        current_state[key] = value
        self.storage.save_state(current_state)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу."""
        current_state = self.storage.retrieve_state()
        return current_state.get(key, None)


def get_states():
    """функция инициации хранилища."""
    storage = JsonFileStorage(STATE_STORAGE_FILE)
    states = State(storage)
    for index in IndexName:
        states.set_state(
            f"last_{index.value}_indexed_modified_at", START_SYNC_TIME
        )
        states.set_state(f"{index.value}_ids", [])
    return states
