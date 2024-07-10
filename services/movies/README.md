# Ограниченный сервис поиска по базе фильмов

Ограничения:

- отсутствует компонент ETL для перекачки фильмов из БД Postrgres сервиса Admin в Elasticsearch
- БД Elasticsearch в папке ./elastic_data

## Запуск сервиса в контейнерах Docker

 1. Создать .env файл из env.example в текущей папке
 2. Запустить Docker
 3. Поднимаем контейнеры:

```bash
docker compose up -d
```
