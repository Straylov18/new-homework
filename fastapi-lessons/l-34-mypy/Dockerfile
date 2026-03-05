FROM python:3.12-alpine

WORKDIR /app

ENV PYTHONPATH .
ENV PYTHONBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apk add --no-cache poetry \
    && apk add --no-cache curl

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY ./src ./src
COPY ./alembic.ini ./alembic.ini
COPY ./migrations ./migrations

EXPOSE 8000

CMD poetry run alembic upgrade head \
    && poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000
