ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR on
ENV PIP_DISABLE_PIP_VERSION_CHECK on

RUN pip install poetry==1.8.3

WORKDIR /app
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root
COPY ./src .
