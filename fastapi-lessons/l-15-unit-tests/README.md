# Unit тесты

[//]: # (TODO зачем тестировать)

## Шаблон простого fastapi приложения

Создадим пример простого fastapi приложения, 
у которого допустим в слое бизнес логики, в **src/service/math_funcs** будут лежать следующие функции:
```python
def my_factorial(n: int):
    if n == 0 or n == 1:
        return 1
    else:
        return n * my_factorial(n - 1)


def divide_and_conquer(num: int, denum: int):
    if denum == 0:
        raise Exception("denum must not be 0!")
    else:
        return f"conquered {num // denum} times"


def get_dominant_color(r: int, g: int, b: int) -> str:
    max_color = max(r, g, b)
    max_colors = []
    if r == g and g == b:
        return 'same'
    if max_color == r:
        max_colors.append('red')
    if max_color == g:
        max_colors.append('green')
    if max_color == b:
        max_colors.append('blue')
    return ', '.join(max_colors)
```

В данном уроке мы напишем автоматические тесты, 
проверяющие работоспособность этих функций изолированно от всего приложения.
Это будут так называемые unit тесты. 
**Unit тесты** - тесты, проверяющие конкретный кусок кода (обычно функцию, метод или класс) 
изолированно от остального приложения.
Проверка обычно происходит на входных данных, для которых известен точный ответ.
В первую очередь на проекте пишут unit тесты, 
потому что:
- ими можно покрыть конкретные участки кода и быть уверенным, 
что проверяется именно этот кусок
- они запускаются быстрее остальных видов тестов, поэтому их можно написать много
- их писать проще всего (почти не нужны дополнительные абстракции для их запуска)

Для написания тестов в python приложениях сейчас наиболее популярна библиотека pytest.

Установим pytest, не забывая положить его в зависимости для тестирования, 
чтобы он не включался в итоговую сборку проекта:
```shell
poetry add pytest --group test
```

Каждый тест будет представлять у нас функцию с префиксом "test_" в имени, 
которая будет вызывать нужный нам кусок кода 
и проверять результат его выполнения с ожидаемым выводом.
Тесты принято класть рядом с папкой **src** в папку **tests**.
Там pytest будет искать их по умолчанию, хотя можно переконфигурировать его и другим способом.

Создадим файл с тестами **tests/test_divide_and_conquer.py** 
и объявим в нем простенькую функцию для тестирования функции divide_and_conquer (из **src/service/math_funcs**).
Мы можем предположить что функция будет выдавать сообщение "conquered 2 times", 
если первый параметр больше второго в 2 раза.
С помощью ключевого слова ```assert``` проверим, что эта логика будет выполняться:
```python
from src.service.math_funcs import divide_and_conquer

def test_divide_and_conquer():
    assert divide_and_conquer(8, 4) == "conquered 2 times"
```

Чтобы запустить тесты, необходимо просто запустить pytest:
```shell
poetry run pytest
```

При таком запуске pytest автоматически найдет и запустит все функции с префиксом "test_" 
во всех файлах с префиксом "test_".

Поскольку сейчас написанный нами тест выполнится успешно, 
pytest выдаст нам следующее сообщение:
```
collected 1 item

tests/test_divide_and_conquer.py::test_divide_and_conquer PASSED [100%]

========================= 1 passed in 0.04s ==========================
```

Если бы в тесте была ошибка, он бы выдал, что тест не проходит успешно 
(и вывел бы какой ответ ожидался бы и какой пришел):
```
collected 1 item

tests/test_divide_and_conquer.py::test_divide_and_conquer FAILED [100%]

============================== FAILURES ==============================
______________________ test_divide_and_conquer _______________________

    def test_divide_and_conquer():
>       assert divide_and_conquer(7, 4) == "conquered 2 times"
E       AssertionError: assert 'conquered 1 times' == 'conquered 2 times'
E
E         - conquered 2 times
E         ?           ^
E         + conquered 1 times
E         ?           ^

tests/test_divide_and_conquer.py:5: AssertionError
========================= 1 failed in 0.15s ==========================
```

Если же необходимо еще больше информации о том, 
почему какие-то тесты не прошли, 
можно запускать pytest с дополнительным параметром "-v":
```shell
poetry run pytest -v
```

Стоит заметить, что выражений assert в одной тестовой функции может быть много:
```python
def test_divide_and_conquer():
    assert divide_and_conquer(8, 4) == "conquered 2 times"
    assert divide_and_conquer(12, 2) == "conquered 6 times"
```
Такой тесть будет считаться выполненным, если все сравнения прошли корректно

### Проверка отработки исключений

Порой также возникает необходимость проверять правильность выдаваемых исключений.

Чтобы разнести проверки логически, 
создадим отдельный тест под проверку исключений в том же файле.

Если второй параметр функции divide_and_conquer является нулем, 
она выдает вполне конкретное исключение и не совершает дальнейшие вычисления.
Проверим что в подобных случаях вызываетс янужное исключение с нужным сообщением:
```python
import pytest

def test_divide_and_conquer_exception():
    with pytest.raises(Exception, match="denum must not be 0!"):
        divide_and_conquer(5, 0)
```
Здесь обертка ```with pytest.raises(Exception, match="denum must not be 0!"):``` 
проверяет что нижестоящий код (```divide_and_conquer(5, 0)```) 
обязан вернуть исключение класса ```Exception``` и сообщением ```"denum must not be 0!"```.

Если мы запустим тесты как и в прошлый раз, 
pytest выполнит оба теста и вернет нам:
```
collected 2 items

tests/test_divide_and_conquer.py ..                            [100%]

========================= 2 passed in 0.05s ==========================
```

## Выборочный запуск тестов

Однако если не хочется запускать все тесты, 
мы можем запустить и только конкретный тест по имени (указав "путь_к_файлу::имя_теста"):
```shell
poetry run pytest tests/test_divide_and_conquer.py::test_divide_and_conquer_exception
```
Тогда запуститься только один конкретный тест:
```
collected 2 items / 1 deselected / 1 selected

tests/test_divide_and_conquer.py .                             [100%]

================== 1 passed, 1 deselected in 0.08s ===================
```

### Запуск тестов по фильтрам (-k)

Можно также запускать только тесты, 
у которых в имени встречается определенный текст, 
с помощью тега "-k" (--keyword):
```shell
poetry run pytest -k divide_and_conquer
```
Команды выше в данном случае запустит оба теста, 
поскольку у них обоих в названии есть текст "divide_and_conquer".

### Запуск тестов с поиском по составным фильтрам

Поскольку ключ "-k" поддерживает обработку сложных логических выражений, 
можно например делать следующие выборки:
- исключать тесты:
```shell
poetry run pytest -k "not exception"
# запустит все тесты, у которых нет текста "exception" в названии
```
- использовать поиск по нескольким текстам через логическое "И" (and), "ИЛИ" (or), например:
```shell
# или
pytest -k "divide_and_conquer or divide_and_conquer_exception"
# и
pytest -k "divide and exception"
```

### Остановка на первом провале

Также порой при отладке полезно использовать параметр "-x", 
чтобы pytest останавливался на первом провале, 
и не пробегал по всем тестам, 
если тестов очень много и не хочется лишний раз ждать.

## Параметризированный запуск тестов через матрицу проверочных значений

Напишем подробный тест для нашей функции факториала 
(рассмотрим пограничные случаи: пару маленьких значений и одно большое).
Сравнивать будем для начала с результатами стандартной функции факториала из пакета math:
```python
import math
from src.service.math_funcs import my_factorial

def test_factorial_using_std_lib():
    assert my_factorial(0) == math.factorial(0)
    assert my_factorial(1) == math.factorial(1)
    assert my_factorial(2) == math.factorial(2)
    assert my_factorial(3) == math.factorial(3)
    assert my_factorial(100) == math.factorial(100)
```

Запустим его:
```python
poetry run pytest -k test_factorial_using_std_lib
```
И pytest выдаст нам, что запустился 1 тест:
```
collected 3 items / 2 deselected / 1 selected

tests/test_factorial.py .                                      [100%]

================== 1 passed, 2 deselected in 0.08s ===================
```

Однако прописывать кучу assert строк не удобно. 
Вместо этого мы можем задать матрицу параметров, 
которые будут передаваться тесту на вход и прокидывать их в аргументы тестовой функции:
```python
@pytest.mark.parametrize("number", [0, 1, 2, 3, 100])
def test_factorial_using_std_lib(number):
    assert my_factorial(number) == math.factorial(number)
```
Здесь:
- при помощи декоратора ```@pytest.mark.parametrize``` задается матрица входных параметров
- первым аргументом декоратора идет название аргумента функции ("number"), 
в который будут пропихиваться значения
- вторым аргументом декоратора идет последовательность значений, 
для каждого элемента которого запустится отдельный тест
(в аргументы тесту будет передан соответствующее значение)
- описание самой функции теста, 
которому на вход будет приходить параметры из матрицы 
(```def test_factorial_using_std_lib(number):```)

Тогда при запуске этого теста мы увидим, что он запустился 5 раз, но каждый раз с разными параметрами:
```
collected 7 items / 2 deselected / 5 selected

tests/test_factorial.py .....                                  [100%]

================== 5 passed, 2 deselected in 0.07s ===================
```
Так что такое задание разных вариантов событий 
через матрицу аргументов будет полезно в дальнейшем, 
когда мы будем запускать тесты в многопоточном режиме 
(тесты смогут отрабатывать сразу на нескольких ядрах процессора, 
а значит потенциально немного быстрее).

### Многомерная матрица входных параметров

Еще частой практикой является параметризация групп параметров теста, 
например для задания входных данных и ожидаемого результата одновременно.

Напишем похожий тест для факториала, 
но теперь он будет сравнивать результаты с результатами стандартной функции, 
а со значениями из матрицы параметров.

Для этого в матрице декораторе параметризации (```@pytest.mark.parametrize```), 
первым параметром укажем несколько аргументов функции через запятую ("number, factorial_result").
Каждый элемент листа у нас тогда будет содержать кортеж из входных аргументов.
Тогда тест будет выглядеть следующим образом:
```python
@pytest.mark.parametrize("number, factorial_result", [
    (0, 1),
    (1, 1),
    (2, 2),
    (3, 6),
    (25, 15511210043330985984000000),
    # (arg1_value, arg2_value),
    # ...
])
def test_factorial_using_precalculated_values(number, factorial_result):
    assert my_factorial(number) == factorial_result
```
Здесь аргументам "number" и "factorial_result" 
будут передавать поочереди значения 0 и 1, потом 1 и 1, потом 2 и 2 итд.

### Кастомные имена для параметризированных тестов

Чтобы легче было понимать какая группа аргументов за что отвечает, 
можно присвоить тестам свои id.
Для этого в декоратор параметризации нужно передать еще лист id тестов:
```python
@pytest.mark.parametrize("number, factorial_result", [
    (0, 1),
    (1, 1),
    (2, 2),
    (3, 6),
    (25, 15511210043330985984000000),
    # (arg1_value, arg2_value),
    # ...
], ids=["проверка 0", "проверка 1", "проверка 2", "проверка 3", "проверка очень большого числа"])
def test_factorial_using_precalculated_values(number, factorial_result):
    assert my_factorial(number) == factorial_result
```

## Запуск тестов в определенном порядке

[//]: # (TODO запуск тестов в определенном порядке)
```shell
poetry add pytest-ordering --group test
```

```python
import pytest
@pytest.mark.run(order=1)
```
