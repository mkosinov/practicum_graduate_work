import datetime
import logging
from time import sleep
from typing import Iterator

import psycopg2
from elasticsearch import Elasticsearch, helpers
from psycopg2.extras import DictCursor
from pydantic import ValidationError

from models import Filmwork, Genre, IndexName, Person
from services import backoff, states
from settings import (
    CHUNK_SIZE,
    DSL,
    ES_HOST,
    ES_PORT,
    INDEX_GENRES_MAPPINGS,
    INDEX_MOVIES_MAPPINGS,
    INDEX_PERSONS_MAPPINGS,
    INDEX_SETTINGS,
    REPEAT_TIME,
    SQL_REQUEST_FILMWORKS,
    SQL_REQUEST_GENRES,
    SQL_REQUEST_PERSONS,
)

logger = logging.getLogger(__name__)


class PostgresConnect:
    """Класс для поюключения к Postgres."""

    def __init__(self) -> None:
        self._connection = None

    @property
    def connection(self):
        """Подключение/переподключение к БД Postgres."""
        if not self._connection or self._connection.closed:
            try:
                self._connection = psycopg2.connect(**DSL)
            except psycopg2.Error as e:
                logger.error(f"Ошибка подключения к PostgreSQL: {e}")
                raise
        return self._connection

    def close(self):
        """Закрытие подключения к Postgres."""
        if self._connection and not self._connection.closed:
            self._connection.close()

    def cursor(self):
        return self.connection.cursor(cursor_factory=DictCursor)


class PostgresExtractor:
    """Класс-метод работы с Postgres."""

    def __init__(self, chunk_size: int) -> None:
        self.connection = PostgresConnect()
        self.chunk_size = chunk_size

    @backoff()
    def extract_data(
        self,
        sql_request: str,
        last_indexed_modified_at: datetime.datetime,
        start_time: datetime.datetime,
        exclude_ids: list,
        ids_list_key: str,
        model,
    ) -> Iterator[dict | None]:
        """Получение данных пачками c исключением индексированных данных."""
        with self.connection.cursor() as cursor:
            try:
                if exclude_ids:
                    sql_request += """
                    AND (uuid not in %(exclude_ids)s OR modified >
                    %(start_time)s)
                    """
                sql_request += """ORDER BY modified DESC;"""
                cursor.execute(
                    sql_request,
                    {
                        "exclude_ids": tuple(exclude_ids),
                        "last_indexed_modified_at": last_indexed_modified_at,
                        "start_time": start_time,
                    },
                )

                while rows := cursor.fetchmany(self.chunk_size):
                    try:
                        yield [model.transform_from_input(row) for row in rows]
                    except ValidationError as e:
                        logger.error(
                            f"Pydantic ошибка валидации в модели {model}: {e}"
                        )
                        continue
                    for data in rows:
                        ids_list = states.get_state(ids_list_key)
                        ids_list.append(data["uuid"])
                        states.set_state(ids_list_key, ids_list)
            except psycopg2.Error as e:
                logger.error(f"Ошибка выполнения SQL запроса: {e}")
                raise
            finally:
                self.connection.close()


class Transformer:
    """Преобразование выборки для загрузки в Elastiicsearch."""

    def transform(self, data: list[dict]) -> list[dict]:
        """Преобразование данных для Elasticsearch."""
        return [row.model_dump() for row in data]


class ElasticsearchLoader:
    """
    Класс-метод сохранения в БД Elasticsearch. При инициализации экземпляра
    проверяет наличие/создает индексы.
    """

    def __init__(self, client: Elasticsearch):
        self.client = client
        if not self.chech_index_exist(IndexName.genres.value):
            self.create_index(IndexName.genres.value, INDEX_GENRES_MAPPINGS)

        if not self.chech_index_exist(IndexName.movies.value):
            self.create_index(IndexName.movies.value, INDEX_MOVIES_MAPPINGS)

        if not self.chech_index_exist(IndexName.persons.value):
            self.create_index(IndexName.persons.value, INDEX_PERSONS_MAPPINGS)

    def chech_index_exist(self, index_name: str):
        """Метод проверки существования индекса."""
        if self.client.indices.exists(index=index_name):
            logger.info(f"Индекс {index_name} существует.")
            return True
        return False

    def create_index(self, index_name: str, mappings):
        """Метод создания индекса."""
        self.client.indices.create(
            index=index_name,
            mappings=mappings,
            settings=INDEX_SETTINGS,
        )
        logger.info(f"Индекс {index_name} создан.")

    @backoff()
    def load(self, index_name: str, data: list[dict]) -> None:
        """Загрузка данных пачками в ElasticSearch."""
        actions = [
            {
                "_index": index_name,
                "_id": row["uuid"],
                "_source": row,
            }
            for row in data
        ]
        try:
            helpers.bulk(self.client, actions)
        except helpers.BulkIndexError as e:
            for i, error in enumerate(e.errors):
                if (
                    "index" in error
                    and "status" in error["index"]
                    and error["index"]["status"] != 200
                ):
                    logger.info(f"Ошибка индексации документа {i}: {error}")

            raise


class ETL:
    def __init__(
        self,
        extractor: PostgresExtractor,
        transformer: Transformer,
        loader: ElasticsearchLoader,
    ) -> None:
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    def run(self) -> None:
        """Пошаговая реализация ETL."""
        try:
            # Проверяем доступность Elasticsearch
            logger.info(self.loader.client.ping())
            start_time = datetime.datetime.now()
            # Запускаем процесс ETL для каждого индекса
            self._etl_movies(
                index_name=IndexName.movies.value, start_time=start_time
            )
            self._etl_genres(
                index_name=IndexName.genres.value, start_time=start_time
            )
            self._etl_persons(
                index_name=IndexName.persons.value, start_time=start_time
            )
        except Exception as e:
            logger.error(f"Ошибка выполнения ETL: {e}")

    def _etl_index(
        self,
        index_name: str,
        start_time,
        sql_request: str,
        model,
    ):
        """Загрузка данных в указанный индекс."""
        exclude_ids = states.get_state(index_name + "_ids")
        last_indexed_key = f"last_{index_name}_indexed_modified_at"
        for batch in self.extractor.extract_data(
            sql_request=sql_request,
            last_indexed_modified_at=states.get_state(last_indexed_key),
            start_time=start_time,
            exclude_ids=exclude_ids,
            ids_list_key=f"{index_name}_ids",
            model=model,
        ):
            data = self.transformer.transform(batch)
            self.loader.load(index_name, data)

        states.set_state(f"{index_name}_ids", [])
        states.set_state(last_indexed_key, str(start_time))

    def _etl_genres(self, index_name, start_time):
        """Загрузка в индекс genres."""
        self._etl_index(
            index_name=index_name,
            start_time=start_time,
            sql_request=SQL_REQUEST_GENRES,
            model=Genre,
        )

    def _etl_movies(self, index_name, start_time):
        """Загрузка в индекс movies."""
        self._etl_index(
            index_name=index_name,
            start_time=start_time,
            sql_request=SQL_REQUEST_FILMWORKS,
            model=Filmwork,
        )

    def _etl_persons(self, index_name, start_time):
        """Загрузка в индекс persons."""
        self._etl_index(
            index_name=index_name,
            start_time=start_time,
            sql_request=SQL_REQUEST_PERSONS,
            model=Person,
        )


@backoff()
def create_elasticsearch_client(host, port) -> Elasticsearch:
    """Создание и перезапуск соединения с elasticsearch."""
    elasticsearch = Elasticsearch(hosts=f"http://{host}:{port}")
    if elasticsearch.ping():
        return elasticsearch


if __name__ == "__main__":
    client = create_elasticsearch_client(host=ES_HOST, port=ES_PORT)
    etl = ETL(
        extractor=PostgresExtractor(chunk_size=CHUNK_SIZE),
        transformer=Transformer(),
        loader=ElasticsearchLoader(
            client=client,
        ),
    )
    while True:
        etl.run()
        sleep(REPEAT_TIME)
