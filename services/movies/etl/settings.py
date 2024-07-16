"""Настройки приложения postgres_to_es."""

import os

from get_docker_secret import get_docker_secret

# Время между опросами изменений.
REPEAT_TIME = 30

# Файл состояний.
STATE_STORAGE_FILE = "states.json"
START_SYNC_TIME = "1900-01-01 00:00:00.000000"

# Параметры логгирования.
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_FILE_NAME = "logs/postgres_to_es.log"
LOG_FILE_SIZE = 10 * 1024 * 1024  # Максимальный размер лог-файлов, байт.
COUNT_LOG_FILES = 5  # Максимальное количество лог файлов.

# Параметры подключения к Postgres
DSL = {
    "dbname": get_docker_secret("admin_postgres_db"),
    "user": get_docker_secret("admin_postgres_user"),
    "password": get_docker_secret("admin_postgres_password"),
    "host": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
    "port": os.environ.get("POSTGRES_PORT", "5432"),
    "options": "-c search_path=content",
}

SQL_REQUEST_FILMWORKS = """
SELECT fw.id AS uuid,
fw.rating AS imdb_rating,
json_object_agg(DISTINCT g.id, g.name) AS genres,
fw.title,
fw.description,
fw.creation_date,
fw.subscribers_only,
concat('[', string_agg(DISTINCT CASE WHEN pfw.role = 'actor' THEN
json_build_object('uuid', p.id, 'full_name', p.full_name) #>> '{}' END, ','),
']') AS actors,
concat('[', string_agg(DISTINCT CASE WHEN pfw.role = 'writer' THEN
json_build_object('uuid', p.id, 'full_name', p.full_name) #>> '{}' END, ','),
']') AS writers,
concat('[', string_agg(DISTINCT CASE WHEN pfw.role = 'director' THEN
json_build_object('uuid', p.id, 'full_name', p.full_name) #>> '{}' END, ','),
']') AS directors,
GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) AS modified
FROM content.film_work as fw
LEFT JOIN content.genre_film_work gfm ON fw.id = gfm.film_work_id
LEFT JOIN content.genre g ON gfm.genre_id = g.id
LEFT JOIN content.person_film_work pfw ON fw.id = pfw.film_work_id
LEFT JOIN content.person p ON pfw.person_id = p.id
GROUP BY uuid
HAVING GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) >
%(last_indexed_modified_at)s
"""

SQL_REQUEST_GENRES = """
SELECT id AS uuid, name, description FROM content.genre
GROUP BY uuid
HAVING modified > %(last_indexed_modified_at)s
"""

SQL_REQUEST_PERSONS = """
SELECT p.id AS uuid, p.full_name AS full_name,
GREATEST(MAX(fw.modified), MAX(p.modified))::TEXT as modified,
COALESCE(json_agg(json_build_object('uuid', pfw.film_work_id, 'title',
fw.title, 'imdb_rating', fw.rating, 'description', fw.description, 
'creation_date', fw.creation_date, 'roles', replace(array_to_string(pfw.roles,
','), ',', ', ')))::TEXT, '[]'::TEXT) AS films
FROM content.person as p
JOIN (SELECT person_id, film_work_id, array_remove(COALESCE(array_agg(DISTINCT
role) FILTER (WHERE role IS NOT NULL), '{}'), NULL) AS roles FROM
content.person_film_work GROUP BY person_id, film_work_id) AS pfw
LEFT JOIN content.film_work fw ON pfw.film_work_id = fw.id
ON p.id = pfw.person_id
GROUP BY p.id
HAVING GREATEST(MAX(fw.modified), MAX(p.modified)) >
%(last_indexed_modified_at)s
"""

CHUNK_SIZE = 100  # Максимальное количество записей в пачке.

# Параметры подключения к Elasticsearch
ES_HOST = os.environ.get("ES_HOST", "127.0.0.1")
ES_PORT = int(os.environ.get("ES_PORT", "9200"))

INDEX_SETTINGS = {
    "refresh_interval": "1s",
    "analysis": {
        "filter": {
            "english_stop": {"type": "stop", "stopwords": "_english_"},
            "english_stemmer": {"type": "stemmer", "language": "english"},
            "english_possessive_stemmer": {
                "type": "stemmer",
                "language": "possessive_english",
            },
            "russian_stop": {"type": "stop", "stopwords": "_russian_"},
            "russian_stemmer": {"type": "stemmer", "language": "russian"},
        },
        "analyzer": {
            "ru_en": {
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "english_stop",
                    "english_stemmer",
                    "english_possessive_stemmer",
                    "russian_stop",
                    "russian_stemmer",
                ],
            }
        },
    },
}

INDEX_GENRES_MAPPINGS = {
    "dynamic": "strict",
    "properties": {
        "uuid": {"type": "keyword"},
        "name": {"type": "keyword"},
        "description": {"type": "text", "analyzer": "ru_en"},
    },
}

INDEX_MOVIES_MAPPINGS = {
    "dynamic": "strict",
    "properties": {
        "uuid": {"type": "keyword"},
        "imdb_rating": {"type": "float"},
        "genre": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "uuid": {"type": "keyword"},
                "name": {"type": "text", "analyzer": "ru_en"},
            },
        },
        "title": {
            "type": "text",
            "analyzer": "ru_en",
            "fields": {"raw": {"type": "keyword"}},
        },
        "description": {"type": "text", "analyzer": "ru_en"},
        "creation_date": {"type": "date", "format": "yyyy"},
        "subscribers_only": {"type": "boolean"},
        "actors": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "uuid": {"type": "keyword"},
                "full_name": {"type": "text", "analyzer": "ru_en"},
            },
        },
        "writers": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "uuid": {"type": "keyword"},
                "full_name": {"type": "text", "analyzer": "ru_en"},
            },
        },
        "directors": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "uuid": {"type": "keyword"},
                "full_name": {"type": "text", "analyzer": "ru_en"},
            },
        },
    },
}

INDEX_PERSONS_MAPPINGS = {
    "dynamic": "strict",
    "properties": {
        "uuid": {"type": "keyword"},
        "full_name": {
            "type": "text",
            "analyzer": "ru_en",
            "fields": {"raw": {"type": "keyword"}},
        },
        "films": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "uuid": {"type": "keyword"},
                "imdb_rating": {"type": "float"},
                "title": {"type": "text", "analyzer": "ru_en"},
                "description": {"type": "text", "analyzer": "ru_en"},
                "creation_date": {"type": "date", "format": "yyyy"},
                "roles": {"type": "text", "analyzer": "ru_en"},
            },
        },
    },
}
