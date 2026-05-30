FROM python:3.12-slim

WORKDIR /usr/src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .

RUN set -xe \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install virtualenvwrapper poetry==1.8.2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

ADD ./src ./src

EXPOSE 8000

CMD poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000
