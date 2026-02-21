# Работа с базами данных

В предыдущих уроках все приложения хранили состояние в оперативной памяти (в себе).
Однако порой необходимо сделать так, чтобы даже при перезапуске приложения данные не терялись.
Обычно для хранения данных к бэку подключают базы данных (далее БД).

**База данных** - это организованная совокупность данных, хранящаяся в специальном виде так, чтобы облегчить их чтение.

Наиболее часто используются реляционные БД. 
В них информация представлена в виде ссылающихся друг на друга таблиц.
Для работы с ними часто использую специальный язык запросов - SQL.

## Модели

**Модель** - это описание объекта, который будет представлять значение таблицы в БД.

У многих современных фреймворков есть механизмы обмена информацией с БД при помощи моделей, описывающих таблицы.

Чтобы бэк мог обмениваться с БД информацией через модели необходимо описать движок работы с БД.
Для этого создадим файл **src/db/session.py** со следующим кодом:
```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from src.config import settings

engine = create_async_engine(url=settings.SQLALCHEMY_DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()
```
Здесь:
- ```engine``` - создание движка работы с конкретной базой данных 
(ссылка на базу данных передается при создании)
- ```async_session_maker``` - асинхронный генератор сессий 
(самих соединений с базой, в рамках которых будет происходить обмен информацией), 
на основе выше созданного движка
- ```Base = declarative_base()``` - базовая описание объекта, 
с помощью которого мы будем описывать содержимое базы данных 

Для описания моделей принято использовать отдельный слой, например **models**.
Опишем модель пользователя:
```python
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.db.session import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
```
Она будет использоваться для обработки информации из таблицы **users** 
(это описано в строчке "__tablename__ = 'users'").
У этой модели описано три поля: id, name, email.
У каждого из них есть свои параметры, 
первый из которых задает тип данных.

Так, **primary_key=True** говорит, 
что данное поле является основным для текущей таблицы 
(таблицы описываемой данной моделью). 
По таким поля БД различает записи между собой при поиске. 
Также такие поля по умолчанию являются уникальными, 
те в таблице не может быть двух сущностей с одинаковым набором primary_key полей.

Если же нужно, чтобы числовой primary_key увеличивался на 1 сам для каждого нового объекта, 
то можно добавить к полю параметр **autoincrement=True**.
Он создаст в БД специальный индекс,
который будет хранить в себе номер следующего элемента 
и увеличиваться на один каждое добавление новой строки в таблицу. 
Этот индекс будет как отдельное внетабличное значение.

Однако вместо id в числовом формате сейчас более широко распространен 
другой способ создания уникальных ключей в таблицах.
Можно каждый раз с помощью специального алгоритма генерировать особый уникальный набор символов без привязки к каким-то индексам - **uid**.
На данный момент один из самых популярных алгоритмов генерации таких uid-ов - UUID4.
Он по умолчанию встроен во многие движки БД.
При таком подходе не будет возникать ситуаций, 
когда индекс наибольшего элемента в таблице собьется
и не будет соответствовать реальности (поскольку в случае генерации uuid, никаких состояний в БД не хранится).

В коде проекта генерация uid будет выглядеть следующим образом:
```python
import uuid
from sqlalchemy import UUID
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.db.session import Base


class User(Base):
    __tablename__ = 'users'

    uid: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
```

## Миграции

**Миграции** - скрипты, позволяющие изменять структуру баз данных. 
Одна миграция хранит в себе информацию о том, как перевести БД из одного состояния в следующее и обратно.

Для начала нужно сгенерировать необходимые файлы для работы с миграциями.
Для этого в корне проекта выполним команду (там же где и pyproject.toml):
```shell
poetry run alembic init -t async migrations
```

Она сгенерит файл **alembic.ini** и папку **migrations**, в которой и будут храниться миграции.

В файле **migrations/env.py** необходимо заменить текст между импортами и методами на:
```python
import sys
from os.path import dirname, abspath

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from src.config import settings
from src.db.session import Base

# should add all models here
from src.models.user import User


target_metadata = Base.metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


# updating database url
configuration = config.get_section(config.config_ini_section, {})
configuration["sqlalchemy.url"] = str(settings.SQLALCHEMY_DATABASE_URL)
```

Также в том же файле в методе запуска миграций (run_async_migrations) необходимо заменить
```python
connectable = async_engine_from_config(
    config.get_section(config.config_ini_section, {}),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
)
```
на
```python
connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
```

Для создания миграции на основе моделей можно использовать команду:
```shell
poetry run alembic revision --autogenerate -m "Initial revision"
```
В данном примере эта команда создаст миграцию, 
которая будет содержать в себе создание таблицы пользователей.

Чтобы применить полученную миграцию к базе данных:
```shell
poetry run alembic upgrade head
```

## Введение в SQL

Все запросы бэкенда (в том числе миграции) перед исполнением в БД на самом деле переводятся в язык SQL.
На нем как минимум полезно уметь писать запросы на получение, вставку, обновление, удаление информации 
(select, insert, update, delete запросы).

Диалекты SQL могут немного отличаться в зависимости от БД 
(postgres, mysql, sqlite, итд. будут иметь свои небольшие отличия).
Поэтому при возникновении вопросов в плане написания запросов, ищи ответы в документации по конкретной БД.

Чтобы набить руку на создании SQL запросов, рекомендуется порешать задачки легкого уровня на leetcode:
https://leetcode.com/problemset/database/.

## Обработка данных БД из python приложения

Чтобы произвести запрос в БД, необходимо открыть сессию взаимодействия с БД.
Чтобы каждый раз не описывать создание этой сессии можно создать генератор сессий в **src/db/session.py**:
```python
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
```

И чтобы не вызывать этот генератор каждый раз, можно например описывать его в методах роутера через зависимость 
(сделать параметру по умолчанию значение Depends(get_session)):
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.schemes.user import UserFromDB
from src.db.session import get_session

@router.get('/list')
async def get_users_list(db_session: AsyncSession = Depends(get_session)) -> list[UserFromDB]:
    query_result = await db_session.execute(select(User))
    return query_result.scalars().all()
```
При вызове описанного выше метода произойдет следующее:
- Откроется сессия.
- В этой сессии выполниться код "select(User)".
Запрос "select(User)" является аналогом SQL запроса "SELECT id, name, email FROM users;" (те автоматом подставляются все поля модели и имя таблицы)
- Код "query_result.scalars().all()" получит все строки из ответа на запрос и переведет данные из них в объекты python.
Поскольку никаких фильтров в запросе не было, эта ручка будет выдавать всю таблицу пользователей.

Ручка для создания объекта в БД же может выглядеть следующим образом:
```python
@router.post('/')
async def create_user(body: UserCreate, db_session: AsyncSession = Depends(get_session)) -> UserFromDB:
    new_user = User(name=body.name, email=body.email)
    db_session.add(new_user)
    await db_session.commit()
    return new_user
```
В ней:
- Создается объект модели при помощи "new_user = User(name=body.name, email=body.email)".
- Он добавляется к списку объектов на внесение изменений в текущей сессии кодом "db_session.add(new_user)" (приложение запоминает, что при фиксации данной сессии необходимо сделать INSERT в таблицу).
- Происходит фиксация сессии через "await db_session.commit()".
- Поскольку после фиксации сессии объект модели обновится в соответствии с данными из БД, 
он уже будет содержать автозаполняемые базой данных поля (id в нашем случае).
Получается new_user вернется уже в том виде, в котором он будет лежать в БД.
