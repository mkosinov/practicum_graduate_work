FROM python:3.11-bullseye

WORKDIR /app

COPY pyproject.toml pyproject.toml
COPY docker-entrypoint.sh docker-entrypoint.sh
RUN pip install --no-cache-dir poetry==1.7.1 && poetry install --no-root

COPY . .

RUN chmod +x docker-entrypoint.sh
ENTRYPOINT [ "/app/docker-entrypoint.sh" ]
