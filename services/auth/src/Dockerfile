ARG PYTHON_FROM=3.12
FROM python:${PYTHON_FROM}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on

WORKDIR /auth-service

RUN pip install poetry
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-root
COPY . .