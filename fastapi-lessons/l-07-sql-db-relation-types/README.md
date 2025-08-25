# Связи между таблицами в реляционных БД

Очень часто при описании каких-то структур данных 
встречается объекты с вложенными в них объектами.
Для представления таких данных в реляционных БД 
можно создавать связи между таблицами через внешние ключи.

Причем реляционные БД особенно удобны в случаях, 
когда вложенные объекты часто повторяются.

Рассмотрим задание таких связей при описании моделей в нашем backend приложении.

## Прямая связь одной таблицы с другой

В случае если необходимо сделать так, 
чтобы на объект из одной таблицы 
ссылалось несколько объектов из другой таблицы, 
можно просто добавить в ссылающиеся таблицы специальное поле-указатель.
Это поле называется внешним ключом (foreign key).
Зачастую в нем хранится просто индекс объекта, на который ссылается текущий объект.
Таким образом задается связь "много к одному" или "один ко многим".

Рассмотрим на примере двух таблиц: user и user_post.

Допустим они имеют следующие модели:
```python
class User(Base):
    __tablename__ = 'user'

    uid: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)

class UserPost(Base):
    __tablename__ = 'user_post'

    uid: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=True)
    date_created: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    user_uid: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("user.uid"), nullable=False)

    user = relationship("User", backref="user_posts")
```
У модели UserPost есть поле user_uid, в котором указано, что это ForeignKey, ссылающийся на поле uid таблицы user (указано как "user.uid"):
```python
user_uid: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("user.uid"), nullable=False)
```
При миграции это поле автоматически создастся как внешний ключ на таблицу user.

Для более удобного мапинга ссылающихся объектов указана дополнительная строчка:
```python
user = relationship("User", backref="user_posts")
```
Благодаря ей в объекте User будут доступны все ссылающиеся на текущего пользователя объекты UserPost по параметру user_ports. 

Стоит не забывать импортировать их в **src/migrations/env.py**, чтобы они включились в следующую миграцию:
```python
from src.models.user import User
from src.models.user_post import UserPost
```

## Связь через промежуточную таблицу (многие ко многим)

Если же необходимо, чтобы при ссылке двух таблиц друг на друга 
у объектов с обеих сторон была возможность иметь много связей, 
необходимо описывать связь немного иначе.
Это стоит делать через отдельную таблицу, 
которая будет содержать пары внешних ключей от обеих таблиц.
Таким образом каждая строка такой таблицей будет описывать одну связь между двумя объектами.

[//]: # (TODO)

## Упрощение конвертирования сложных моделей в схемы

[//]: # (TODO)
