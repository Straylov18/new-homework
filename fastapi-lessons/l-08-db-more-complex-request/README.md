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

Рассмотрим запросы на получения списков сущностей.
Они обычно есть во всех приложениях, 
и в них часто встречаются весьма стандартные фильтры.

Зададим pydantic схему, 
которая будет содежать в себе 
описание передаваемых с фронта фильтров 
для получения списков пользователей:
```python
class Filters(BaseModel):
    search_str: str | None = Field(description="Search by text in user parameters", default=None)
    limit: int | None = Field(description="Limit", default=10)
    offset: int | None = Field(description="Offset", default=0)
    order_by: str | None = Field(description="Order by", default="name")
    date_created__gte: datetime | None = Field(description="Show only users created after date", default=None)
    date_created__lte: datetime | None = Field(description="Show only users created before date", default=None)
    email__in: list[str] | None = Field(description="Email in list", default=None)
```

Здесь указаны достаточно классические фильтры.
Рассмотрим их дальше по отдельности.

### Пагинация (limit, offset)

Обычно принято выдавать списки данных для каких-то страниц на фронте или для бесконечных лент например.
В таких случаях данные выдаются кусками (постранично).

Для этого обычно при запросе указывается с какого по какой объект нужно выдавать сущности.

Тогда в ручке на получение листа пользователей будет следующая реализация запроса к базе:
```python
@router.post('/list')
async def get_users_list(filters: Filters, db_session: AsyncSession = Depends(get_session)) -> list[UserFromDB]:
    query = select(User)
    if filters.limit is not None and filters.limit >= 0:
        query = query.limit(filters.limit)
    if filters.offset is not None:
        query = query.offset(filters.offset)

    query_result = await db_session.execute(query)
    return query_result.scalars().all()
```

В данном случае если лимит указан отрицательным будут выгружаться все данные.
Порой возможность выгрузки всех данных убирают.

### Сортировка (order_by, order_desc)

[//]: # (TODO order_by asc desc)

### Строка текстового поиска

Для поиска по тексту объекта обычно делают отдельный параметр запроса.
Обычно поиск делают без учета верхнего / нижнего регистра символов 
и делают еге через операцию 'or' по всем текстовым полям отдельно.

в коде обработки ручки эту будет выглядеть:
```python
if filters.search_str is not None:
    query = query.filter(
        or_(
            User.name.ilike(f"%{filters.search_str}%"),
            User.email.ilike(f"%{filters.search_str}%"),
        )
    )
```
В указанном выше коде:
- 'or_' задает необходимость выполнения одного из условий поиска,
- ilike сравнивать поле, из которого оно вызывается 
(в данном случае поля name и email модели User). 
В отличие от like (поиск по тексту с использованием wildcard вырадений), 
ilike не будет учитывать различия в заглавных и строчных буквах.
- поскольку значения в ilike обрамлены в '%' искомый текст не обязательно должен полностью совпадать, 
а может быть и всего лишь подстрокой в поле таблицы. 

### Фильтры больше меньше по датам (date_created__gte, date_created__lte)

[//]: # (TODO date filter)

### Фильтры по листам данных (email__in)

[//]: # (TODO email in list)

Подробнее о запросах со сложными выборками можно почитать тут: 
https://docs.sqlalchemy.org/en/20/tutorial/data_select.html.

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
