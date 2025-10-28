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

## Как БД понимает когда использовать индексы

Движок базы данных сам решает какие алгоритмы поиска использовать для конкретного запроса.
В том числе движок БД сама понимает 
когда она сможет использовать тот или иной индекс для ускорения операций с данными.

Рассмотрим на примере работы PostgreSQL все этапы "подкапотной части" обработки запроса.

Сперва postgres запускает планировщик запросов, 
который оценивает сложность всех операций в запросе при решении их различными алгоритмами.
Это может занимать приличное количество времени, 
поэтому здесь всегда ищется баланс между поиском самого оптимального результата 
и временем планирования.

Настройки планировщика postgresа можно видоизменять в его конфигах.
Эти изменения будут доступны после перезапуска postgresа.
Этого мы пока делать не будет и воспользуемся настройками по умолчанию.
До момента, пока твое приложение столкнется с большими нагрузками, 
не рекомендуется подкручивать настройки планировщика запросов.

Как же понять сколько времени ушло на планирование запроса и на конкретные операции в нем?
Для этого можно воспользоваться командой анализа запроса.

## Анализ сложности запросов к БД

Допустим мы увидели в логах нашего приложения какой SQL запрос оно отправило БД.
Мы можем запустить такой запрос через консоль postgresа, 
обернув этот запрос в **EXPLAIN ANALYZE (анализируемый запрос)**.

Пусть есть запрос получения списка записей из user_post таблицы:
```sql
SELECT *
FROM user_post
-- WHERE user_post.title = 'some post 1'
WHERE user_post.number_of_updates = 1
ORDER BY user_post.title
LIMIT 10 OFFSET 0
;
```
Этот запрос возвращает первые 10 элементов отфильтрованного списка постов пользователей, 
которые редактировались только один раз (number_of_updates = 1). 
Записи должны быть отсортированы по полю title 
(соответственно будут выдаваться первые 10 элементов отсортированного списка).

Чтобы проанализировать, что сделал движок postgres для выполнения этого запроса добавим EXPLAIN ANALYZE:
```sql
EXPLAIN ANALYZE
(
    SELECT *
    FROM user_post
    WHERE user_post.number_of_updates = 1
    ORDER BY user_post.title
    LIMIT 10 OFFSET 0
);
```

Тогда postgres вернет вот такой анализ:
```
Limit  (cost=17.52..17.53 rows=3 width=108) (actual time=0.084..0.088 rows=7 loops=1)
  ->  Sort  (cost=17.52..17.53 rows=3 width=108) (actual time=0.083..0.085 rows=7 loops=1)
        Sort Key: title
        Sort Method: quicksort  Memory: 25kB
        ->  Seq Scan on user_post  (cost=0.00..17.50 rows=3 width=108) (actual time=0.022..0.026 rows=7 loops=1)
              Filter: (number_of_updates = 1)
              Rows Removed by Filter: 1
Planning Time: 0.196 ms
Execution Time: 0.119 ms
```
Здесь видно, что:
- Планировщик потратил 0.196 миллисекунд перед началом запроса 
(Planning Time: 0.196 ms)
- На саму обработку же запроса postgres потратил 0.119 миллисекунд 
(Execution Time: 0.119 ms)
- Какую сложность (в условных единицах postgres) планировщик оценивал каждую операцию 
(значение "cost" в скобках после указания типа операции)
- Сколько операция заняла в итоге 
(значение "actual time" в строках типа операции)
- Какие алгоритмы postgres использовал по итогу для каких операций
Видно, что для сортировки он использовал "quicksort", 
а для прохода по строкам таблицы он использовал "Seq Scan" (sequential scan или простой обходит таблицы подряд).
- Видно фильтры по каким полям сколько строк отсеяли (Rows Removed by Filter: 1)

Попробуем проанализировать аналогичный запрос, 
но будем теперь фильтровать по полю, 
для которого мы создавали индекс:
```sql
EXPLAIN ANALYZE
(
    SELECT *
    FROM user_post
    WHERE user_post.title = 'some post 1'
    ORDER BY user_post.title
    LIMIT 10 OFFSET 0
);
```

Теперь мы получим следующий результат:
```
Limit  (cost=4.17..11.28 rows=3 width=108) (actual time=0.026..0.028 rows=1 loops=1)
  ->  Bitmap Heap Scan on user_post  (cost=4.17..11.28 rows=3 width=108) (actual time=0.025..0.026 rows=1 loops=1)
        Recheck Cond: ((title)::text = 'some post 1'::text)
        Heap Blocks: exact=1
        ->  Bitmap Index Scan on title_index  (cost=0.00..4.17 rows=3 width=0) (actual time=0.019..0.019 rows=1 loops=1)
              Index Cond: ((title)::text = 'some post 1'::text)
Planning Time: 0.098 ms
Execution Time: 0.054 ms
```
Здесь postgres использует 'Bitmap Index Scan' (поиск по индексу) 
вместо 'Seq Scan', и запрос выполняется сильно быстрее.

Поиграемся еще с запросами, сделаем более сложный фильтр с условием 'OR':
```sql
EXPLAIN ANALYZE
(
    SELECT *
    FROM user_post
    WHERE user_post.title = 'some post 5' OR user_post.title = 'some post 1'
    ORDER BY user_post.title
    LIMIT 10 OFFSET 0
);
```

Тогда postgres будет выполнять два поиска по индексу 
(поскольку данные для обоих условиий могут быть найдены по индексу):
```
Limit  (cost=17.91..17.92 rows=6 width=108) (actual time=0.076..0.079 rows=4 loops=1)
  ->  Sort  (cost=17.91..17.92 rows=6 width=108) (actual time=0.074..0.076 rows=4 loops=1)
        Sort Key: title
        Sort Method: quicksort  Memory: 25kB
        ->  Bitmap Heap Scan on user_post  (cost=8.35..17.83 rows=6 width=108) (actual time=0.029..0.032 rows=4 loops=1)
              Recheck Cond: (((title)::text = 'some post 5'::text) OR ((title)::text = 'some post 1'::text))
              Heap Blocks: exact=1
              ->  BitmapOr  (cost=8.35..8.35 rows=6 width=0) (actual time=0.021..0.022 rows=0 loops=1)
                    ->  Bitmap Index Scan on title_index  (cost=0.00..4.17 rows=3 width=0) (actual time=0.015..0.016 rows=4 loops=1)
                          Index Cond: ((title)::text = 'some post 5'::text)
                    ->  Bitmap Index Scan on title_index  (cost=0.00..4.17 rows=3 width=0) (actual time=0.005..0.005 rows=1 loops=1)
                          Index Cond: ((title)::text = 'some post 1'::text)
Planning Time: 0.388 ms
Execution Time: 0.129 ms
```

Однако если для второго условия 'OR' у нас не будет индекса,
то будет использовать уже обычный перебор и никакого ускорения не произойдет
Те если запрос будет:
```sql
EXPLAIN ANALYZE
(
    SELECT *
    FROM user_post
    WHERE user_post.text = 'df2wewfwf' OR user_post.title = 'some post 5'
    ORDER BY user_post.title
    LIMIT 10 OFFSET 0
);
```

То его обработка будет следующая:
```
Limit  (cost=19.08..19.09 rows=6 width=108) (actual time=0.034..0.037 rows=3 loops=1)
  ->  Sort  (cost=19.08..19.09 rows=6 width=108) (actual time=0.033..0.034 rows=3 loops=1)
        Sort Key: title
        Sort Method: quicksort  Memory: 25kB
        ->  Seq Scan on user_post  (cost=0.00..19.00 rows=6 width=108) (actual time=0.020..0.022 rows=3 loops=1)
              Filter: (((text)::text = 'df2wewfwf'::text) OR ((title)::text = 'some post 5'::text))
              Rows Removed by Filter: 7
Planning Time: 0.168 ms
Execution Time: 0.061 ms
```

Так что стоит помнить, 
что индексы это не панацея и их надо использовать с умом, 
когда в этом появляется необходимость, 
тк. они занимают дополнительное место на диске.
Десятки индексов для табличек с миллионами строк могут суммарно весит сотни мегабайт.

Поэтому если нагрузка на бэк стала достаточно большой, 
чтобы запросы местами начали тормозить, 
то тогда есть смысл использовать 'EXPLAIN ANALYZE', 
чтобы проверить в каких конкретно местах возникает большая нагрузка.
Узнав где БД не справляется можно по ситуации сделать одно из действий:
- добавить туда индексы
- изменить структуру самого запроса, переписав его на запрос поменьше 
(избавляясь от большого количества подзапросов)
- возможно получать данные из БД при помощи нескольких запросов поменьше
