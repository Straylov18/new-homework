# Аргументы таблиц в реляционных БД

Разберем дополнительные аргументы таблиц на примере проекта из 7-го урока.

## Индексы

Чтобы БД быстрее выполняла поиск по каким-то часто фильтруемым полям, 
к таблице можно добавить индекс. 
Индекс будет занимать дополнительное место на диске 
пропорциональное количеству записей в таблице, 
однако будет ускорять простые операции поиска по указанным колонкам.

Добавим таблице UserPost индекс по полю title в моделях:
```python
class UserPost(Base):
    __tablename__ = 'user_post'
    __table_args__ = (
        Index('title_index', 'title'),
    )

    uid: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    ...
```
Здесь создается индекс с названием title_index (первый аргумент), 
и перечислением полей по которым в БД должен считаться индекс.

Чтобы этот индекс вступил в силу, 
потом его естественно необходимо добавить в миграции.

Индекс в postgresql по умолчанию являются бинарными деревьями, 
однако можно использовать и другие виды индексов, 
поддерживаемых самой БД.

Подробнее о видах индексов postgresql можно почитать тут:
https://www.postgresql.org/docs/current/indexes.html.

Также можно создавать индексацию и по связке полей, если ожидается, 
что запросы будут очень часто идти с фильтрацией сразу по нескольким указанным полям:
```python
class UserPost(Base):
    __tablename__ = 'user_post'
    __table_args__ = (
        Index('title_index', 'title'),
        Index('date_created_user_uid_index', 'date_created', 'user_uid'),
    )

    uid: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=True)
    date_created: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    user_uid: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("user.uid"), nullable=False)

    user = relationship("User", backref="user_posts")
```

## Ограничения

В 7-м уроке мы уже познакомились с ограничением на уникальность комбинаций колонок таблиц.
Однако таких ограничений можно выставлять много.

Например, выставим ограничение, чтобы поле number_of_updates всегда было неотрицательным:
```python
class UserPost(Base):
    __tablename__ = 'user_post'
    __table_args__ = (
        Index('title_index', 'title'),
        Index('date_created_user_uid_index', 'date_created', 'user_uid'),
        CheckConstraint('number_of_updates > 0', 'number_of_updates should pe more than 0')
    )
    ...
    number_of_updates: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    ...
```
Здесь сначала задается само условие ('number_of_updates > 0'), 
а потом его описание ('number_of_updates should pe more than 0').

Теперь, после применения миграций с этими изменениями, 
БД не даст создавать строки с number_of_updates <= 0.

Подробнее об описании дополнительных аргументов таблиц БД через модели можно почитать тут:
https://docs.sqlalchemy.org/en/20/core/constraints.html.

## Анализ сложности запросов к БД

[//]: # (TODO EXPLAIN ANALYZE (SELECT ...)
