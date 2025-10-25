# Расширенная фильтрация и анализ генерируемых SQL запросов

## Запуск приложения из прошлого урока

Запустим БД:
```shell
./start_postgres_in_docker.sh
```

Накатим миграции:
```shell
poetry run alembic upgrade head
```

Запустим проект:
```shell
poetry run uvicorn src.main:app --reload
```

## Добавление фильтров

[//]: # (TODO)

## Анализ генерируемых SQL запросов

Как и говорилось ранее, под капотом sqlalchemy конвертирует код в sql запросы.
Каждая новая сессия оборачивается в транзакцию. 
Порой для оптимизации запросов необходимо понимать, 
как будут выглядеть итоговые сгенерированные sql запросы.

Чтобы sqlalchemy выводил в логи все SQL запросы к БД, которые он выполняет, 
необходимо в движке генератора сессий create_async_engine 
(в данном проекте описан в **src/db/session.py**) 
добавить параметр "echo=True":  
```python
engine = create_async_engine(url=settings.DB.SQLALCHEMY_DATABASE_URI, echo=True)
```
Тогда например при создании пользователя 
в логах будет отображаться информация о прошедших SQl запросах:
```
2025-10-25 05:50:29,550 INFO sqlalchemy.engine.Engine select pg_catalog.version()
2025-10-25 05:50:29,550 INFO sqlalchemy.engine.Engine [raw sql] {}
2025-10-25 05:50:29,552 INFO sqlalchemy.engine.Engine select current_schema()
2025-10-25 05:50:29,553 INFO sqlalchemy.engine.Engine [raw sql] {}
2025-10-25 05:50:29,554 INFO sqlalchemy.engine.Engine show standard_conforming_strings
2025-10-25 05:50:29,554 INFO sqlalchemy.engine.Engine [raw sql] {}
2025-10-25 05:50:29,559 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-10-25 05:50:29,561 INFO sqlalchemy.engine.Engine INSERT INTO users (name, email) VALUES (%(name)s::VARCHAR, %(email)s::VARCHAR) RETURNING users.id
2025-10-25 05:50:29,561 INFO sqlalchemy.engine.Engine [generated in 0.00024s] {'name': 'string', 'email': 'string'}
2025-10-25 05:50:29,564 INFO sqlalchemy.engine.Engine COMMIT
```
Как видно здесь сам запрос выполнялся между началом и коммитом транзакции 
("INSERT INTO users ..." был между BEGIN и COMMIT).
Перед этим sqlalchemy получила необходимую для работы с БД информацию.
