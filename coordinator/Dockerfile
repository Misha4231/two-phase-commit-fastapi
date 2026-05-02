FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install poetry

COPY common /app/common
COPY coordinator/pyproject.toml coordinator/poetry.lock* /app/coordinator/

WORKDIR /app/coordinator
RUN poetry config virtualenvs.create false && poetry install --no-root

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app

# install pg client for pg_ready
RUN apt-get update && apt-get install -y postgresql-client

COPY --from=builder /usr/local /usr/local

COPY wait-for-db.sh /app/wait-for-db.sh
COPY common/ /app/common
COPY coordinator/ /app/coordinator

EXPOSE 8000
