FROM python:3.12-slim

WORKDIR /usr/src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .


# Install dependencies
# curl for healthchecks
RUN set -xe \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && apt-get install -y curl \
    && pip install virtualenvwrapper poetry==1.8.2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

ADD ./src ./src
ADD ./alembic.ini ./alembic.ini
ADD ./migrations ./migrations

EXPOSE 8000

ENV PYTHONPATH .

CMD poetry run python3 src/main.py
