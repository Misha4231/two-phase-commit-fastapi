FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install poetry
COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false && poetry install --no-root

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app

# install pg client for pg_ready
RUN apt-get update && apt-get install -y postgresql-client

COPY --from=builder /usr/local /usr/local
COPY . /app

EXPOSE 8000
