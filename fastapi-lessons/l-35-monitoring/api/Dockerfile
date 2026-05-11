FROM python:3.12-alpine

WORKDIR /app

ENV PYTHONPATH .
ENV PYTHONBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apk add --no-cache uv \
    && apk add --no-cache curl

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev --no-group test

COPY ./src ./src

EXPOSE 8000

CMD uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
