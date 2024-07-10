# ASYNC_API_sprint_1

# Адрес репозитория:
https://github.com/mkosinov/Async_API_sprint_1

# Авторы проекта:
Гельруд Борис (https://github.com/Izrekatel/)
Косинов Максим (https://github.com/mkosinov)
Холкин Сергей (https://github.com/Khosep)

## Описание проекта:
"ASYNC_API" - ассинхронный API для онлайн-кинотеатра учебного проекта
Яндекс.Практикум, состоящий из двух сервисов:
1. ETL сервис, который забирает данные по кинопроизведениям, жанрам и персонам
из БД Postgres и индексирует их в Elasticsearch.
2. API на Fastapi, которое получает данные из Elasticsearch и кэширует в
Redis.
Проект организован в docker-compose.

## Стек:
- Python
- PostgreSQL
- Elasticsearch
- Redis
- Fastapi
- Git
- Docker
- Poetry
- Pre-commit
- Pydantic
- Psycopg2-binary
- Uvicorn

### 1. Запуск проекта в контейнерах Docker

#### 1. Создать .env файл из env.example (в корневой папке)

#### 2. Запустить Docker

#### 3. Поднимаем контейнеры:
```bash
docker-compose up -d --build
```
#### 4. Локальные адреса проекта:
```
Адрес API
```
http://127.0.0.1/api/v1/
```
Документация API
```
http://127.0.0.1/api/openapi/
```

### 2. Установка для локальной разработки

1. Установите Poetry

Для Linux, macOS, Windows (WSL):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Для Windows (Powershell):
```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
Чтобы скрипты выполнялись, PowerShell может попросить у вас поменять политики.

В macOS и Windows сценарий установки предложит добавить папку с исполняемым файлом poetry в переменную PATH. Сделайте это, выполнив следующую команду:

macOS (не забудьте поменять borisgelrud на имя вашего пользователя)
```bash
export PATH="/Users/borisgelrud/.local/bin:$PATH"
```

Windows
```bash
$Env:Path += ";C:\Users\borisgelrud\AppData\Roaming\Python\Scripts"; setx PATH "$Env:Path"
```

Для проверки установки выполните следующую команду:
```bash
poetry --version
```
Опционально! Изменить местонахождение окружения в папке проекта
```bash
poetry config virtualenvs.in-project true
```

Установка автодополнений bash (опцонально)
```bash
poetry completions bash >> ~/.bash_completion
```

Создание виртуально окружения
```bash
poetry env use python3.11
```

2. Установите виртуальное окружение
Важно: poetry ставится и запускается для каждого сервиса отдельно.

Перейти в одну из папок сервиса, например:
```bash
cd bot
```

Установка зависимостей (для разработки)
```bash
poetry install
```

Запуск оболочки и активация виртуального окружения

```bash
your@device:~/your_project_pwd/your_service$ poetry shell
```

Проверка активации виртуального окружения
```bash
poetry env list
```


* Полная документация: https://python-poetry.org/docs/#installation
* Настройка для pycharm: https://www.jetbrains.com/help/pycharm/poetry.html


3. Установка pre-commit

Модуль pre-commit уже добавлен в lock, таким образом после настройки виртуального окружения, должен установится автоматически.
Проверить установку pre-commit можно командой (при активированном виртуальном окружении):
```bash
pre-commit --version
```

Если pre-commit не найден, то его нужно установить по документации https://pre-commit.com/#install

```bash
poetry add pre-commit
```

4. Установка hook

Установка осуществляется hook командой
```bash
pre-commit install --all
```

В дальнейшем при выполнении команды `git commit` будут выполняться проверки перечисленные в файле `.pre-commit-config.yaml`.


5. Запуск backend сервера Fastapi (после запуска всего проекта в контейнерах Docker)

#### 1. Изменить значение ES_HOST на "localhost" в .env

#### 2. Войти в папку fastapi
```bash
cd fastapi
```
#### 3. Войти в оболочку виртуального окружения poetry
```bash
poetry shell
```

#### 4. Запустить локальный backend сервер fastapi
```poetry
python main.py
```
#### 5. Адреса API локального backend сервера fastapi

Локальные адреса проекта:

Адрес API
```
http://127.0.0.1:8000/api/v1/
```
Документация API
```
http://127.0.0.1:8000/api/openapi/
```

### Примеры запросов API:

* http://127.0.0.1/api/v1/films?sort=-imdb_rating&page_size=50&page_number=1

Пример ответа:
```
{
  "uuid": "uuid",
  "title": "str",
  "imdb_rating": "float"
},
...
[
{
  "uuid": "524e4331-e14b-24d3-a156-426614174003",
  "title": "Ringo Rocket Star and His Song for Yuri Gagarin",
  "imdb_rating": 9.4
},
{
  "uuid": "524e4331-e14b-24d3-a156-426614174003",
  "title": "Lunar: The Silver Star",
  "imdb_rating": 9.2
},
...
]
```
* http://127.0.0.1/api/v1/genres/

Пример ответа:
```
[
{
  "uuid": "uuid",
  "name": "str",
  ...
},
...
]

[
{
  "uuid": "d007f2f8-4d45-4902-8ee0-067bae469161",
  "name": "Adventure",
  ...
},
{
  "uuid": "dc07f2f8-4d45-4902-8ee0-067bae469164",
  "name": "Fantasy",
  ...
},
...
]
```
