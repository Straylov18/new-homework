# Настройка информативных логов для backend приложения

Стандартные логи приложения будут не очень информативны.
Как минимум в них нет даты и времени, 
поэтому сложнее (почти невозможно) 
будет разбираться с ошибками в системе, работающей на продуктивном сервере.

## Настройка логов при помощи словаря

Возьмем проект из прошлого урока и настроем ему формат логирования.

Добавим настройки логов в конфиг нашего проекта:
```python
import logging.config

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"default": {"format": "%(asctime)s [%(process)s] %(levelname)s: %(message)s"}},
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": "INFO",
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "gunicorn": {"propagate": True},
        "gunicorn.access": {"propagate": True},
        "gunicorn.error": {"propagate": True},
        "uvicorn": {"propagate": True},
        "uvicorn.access": {"propagate": True},
        "uvicorn.error": {"propagate": True},
    },
}

logging.config.dictConfig(LOG_CONFIG)
```
Здесь настройки логирования берутся из словаря.
В данных настройках указывается например:
- стиль форматирования логов в поле **formatters**
- описание того, на сколько подробно писать логи в поле **level**
- описание базового описания логов в приложении в **root**
- логеры библиотек, на которые будут распространятся данные настройки в поле **loggers**

## Уровни логов

Существует несколько уровней вывода логов:
- DEBUG (вывод информации при запуске приложения в режиме отладки)
- INFO (вывод информамции об успешных действиях)
- WARNING (вывод предупреждений)
- ERROR (вывод ошибок)
- CRITICAL (вывод критических ошибок)

При определении уровня логов будут выводиться логи имеющие статус указанного уровня или ниже
(при уровне ERROR будут выводиться логи типов ERROR и CRITICAL).

Это сделано потому что при отладке приложения необходимо видеть одни логи, 
а при работе приложения у заказчика зачастую другие.

Подтянем информацию о том, 
насколько подробные логи необходимо писать из переменных окружения.
Для этого зададим LOG_LEVEL в **.env** фале:
```.env
# LOG_LEVEL="DEBUG"
LOG_LEVEL="INFO"
# LOG_LEVEL="WARNING"
# LOG_LEVEL="ERROR"
# LOG_LEVEL="CRITICAL"
```
и будем использовать ее в конфигах проекта:
```python
from pydantic_settings import SettingsConfigDict, BaseSettings
import logging.config


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    BASE_ROUTE_PATH: str = '/api/v1'
    LOG_LEVEL: str = 'INFO'


settings = Settings()


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"default": {"format": "%(asctime)s [%(process)s] %(levelname)s: %(message)s"}},
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": settings.LOG_LEVEL,
        }
    },
    "root": {"handlers": ["console"], "level": settings.LOG_LEVEL},
    "loggers": {
        "gunicorn": {"propagate": True},
        "gunicorn.access": {"propagate": True},
        "gunicorn.error": {"propagate": True},
        "uvicorn": {"propagate": True},
        "uvicorn.access": {"propagate": True},
        "uvicorn.error": {"propagate": True},
    },
}

logging.config.dictConfig(LOG_CONFIG)
```

## Определение своего класса форматирования логов

[//]: # (TODO)

```python
import logging

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

logger = logging.getLogger("l-11-logs-format")
logger.setLevel(logging.INFO)

# create console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

console_handler.setFormatter(CustomFormatter())

logger.addHandler(console_handler)
```

```python
logger.debug("debug message")
logger.info("info message")
logger.warning("warning message")
logger.error("error message")
logger.critical("critical message")
```
