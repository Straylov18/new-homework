# Базовый образ Python.
FROM python:3.12-slim

# Не создавать .pyc файлы и не буферизовать вывод (логи видны сразу).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Сначала копируем только файлы зависимостей, чтобы кэш слоёв docker
# не сбрасывался при каждом изменении исходников.
COPY pyproject.toml ./

# Устанавливаем зависимости. pip-install из pyproject (без poetry в рантайме).
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        "fastapi>=0.129,<0.130" \
        "uvicorn[standard]>=0.40,<0.41" \
        "arq>=0.26,<1.0" \
        "redis>=4.2,<6" \
        "pydantic>=2.7,<3.0" \
        "pydantic-settings>=2.13,<3.0" \
        "email-validator>=2.1,<3.0"

# Копируем исходники приложения.
COPY . .

# Команда по умолчанию — запуск FastAPI (uvicorn).
# В docker-compose для сервиса arq-worker она переопределяется.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
