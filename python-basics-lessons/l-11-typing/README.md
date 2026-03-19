# Указание типов данных в python 

Одной из особенностей python является автоматическое присвоение типов.
Из-за этой особенности python не требует явно указывать типы переменных.
Однако часто можно встретить код, в котором типы таки указаны явно.
Это делается потому что явное указание типов позволяет:
- улучшить читаемость кода
- обнаружить ошибки на этапе разработки 
  (с помощью инструментов статического анализа, например, **mypy**, 
с которым мы подробнее познакомимся в курсе по fastapi)
- облегчить работу IDE (улучшает качество подсказок и автодополнения)

## Typing

Указание типов в python делается при помощи встроенного модуля typing.

Так например можно задавать составные типы листов, словарей, кортежей, сетов, итд.:
```python
from typing import List, Dict, Tuple, Set

# листы
numbers: List[int] = [1, 2, 3, 4, 5]
names: List[str] = ["Biba", "Boba"]

# словари
person: Dict[str, int] = {"age": 30, "height": 180}

# кортежи
coordinates: Tuple[float, float] = (3.5, 7.2)

# Сеты
unique_numbers: Set[int] = {1, 2, 3}
```

Можно показывать, что значение может быть ```None``` при помощи ```Optional```:
```python
from typing import Optional

def greet(name: Optional[str] = None) -> str:
    if name is None:
        return "Даров, кто бы то не был!"
    return f"Здаров, {name}!"

print(greet())
# выведет "Даров, кто бы то не был!"
print(greet("Папич"))
# выведет "Здаров, Папич!"
```
Здесь функция ```greet``` принимает либо строки либо ```None```. 

Также можно делать составные типы через ```Union```, 
чтобы типом мог быть один из указанных типов на выбор:
```python
from typing import Union

def handle_data(data: Union[str, int]) -> str:
    if isinstance(data, str):
        return f"Строка: {data}"
    elif isinstance(data, int):
        return f"Чисто: {data}"

print(handle_data("строка"))
# Строка: строка
print(handle_data(42))
# Чисто: 42
```
Здесь функция ```handle_data``` работает как со строками, так и с числами.

Также можно задавать собственные типы данных:
```python
from typing import TypeAlias

# Зададим свои типы данных для точки и группы точек
Point: TypeAlias = Tuple[float, float]
Points: TypeAlias = List[Point]
# По сути теперь Point это просто сокращение от Tuple[float, float]

def calculate_distance(p1: Point, p2: Point) -> float:
    x1, y1 = p1
    x2, y2 = p2
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

points: Points = [(0.0, 0.0), (3.0, 4.0)]
distance = calculate_distance(points[0], points[1])
print(distance)  
# выдаст 5.0
```
Здесь тип ```Point``` является сокращением типа ```Tuple[float, float]```, 
а тип ```Points``` является сокращением типа ```List[Point]```.

Также можно создавать классы и функции, 
работающие с разными типами данных при помощи ```Generic```:
```python
from typing import TypeVar, Generic

T = TypeVar('T')

# Если ты хочешь, чтобы тип был обязательно унаследован от твоего базового класса BaseClass: 
# T = TypeVar("T", bound=BaseClass)

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

# Реализуем стак, хранящий в себе числа
int_stack = Stack[int]()
int_stack.push(1)
int_stack.push(2)
print(int_stack.pop())  
# вернет 2

# Реализуем стак, хранящий в себе строки
str_stack = Stack[str]()
str_stack.push("где я?")
str_stack.push("кто я?")
print(str_stack.pop())  
# вернет "кто я?"
```
Здесь сначала задается шаблон типа (```T = TypeVar('T')```),
потом он указывается в классе через ```Generic```.
Дальше на основе класса ```Stack``` делается два объекта:
- один хранит и обрабатывает во всех своих методах числа (```Stack[int]()```)
- другой хранит и обрабатывает во всех своих методах строки (```Stack[str]()```)

Можно указывать тип передаваемой функции, ее аргументов и вывода при помощи ```Callable```:
```python
from typing import Callable

def apply_operation(x: int, y: int, operation: Callable[[int, int], int]) -> int:
    # Здесь мы говорим, что в переменную operation на вход будет приходить функция с 2 числовыми аргументами, возвращающая число
    return operation(x, y)

def add(a: int, b: int) -> int:
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b

print(apply_operation(3, 4, add))
# выдаст 7
print(apply_operation(3, 4, multiply))
# выдаст 12
```
Здесь ```Callable[[int, int], int]``` указывает функцию, 
принимающую на вход два числовых аргумента и выдающую число.

Можно также указывать какой набор значений может принимать переменная при помощи ```Literal```:
```python
from typing import Literal

def set_mode(mode: Literal["read", "write", "append"]) -> None:
    print(f"Mode set to {mode}")

set_mode("read")
set_mode("write")
set_mode("append")
```
Здесь при указании ```mode: Literal["read", "write", "append"]``` предполагается, 
что переменная ```mode``` будет принимать одно из трех значений ```"read", "write", "append"```.

Можно указывать, что переменная не должна изменять при помощи ```Final```:
```python
from typing import Final

MAX_USERS: Final[int] = 100
# Теперь при изменении MAX_USERS mypy будет подсвечивать строку с изменение как ошибку
```
