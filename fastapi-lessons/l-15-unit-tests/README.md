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
Unit тесты - тесты, проверяющие конкретный кусок кода (обычно функцию, метод или класс) 
изолированно от остального приложения.
Проверка обычно происходит на входных данных, для которых известен точный ответ.

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

[//]: # (TODO)
[//]: # (TODO проверка отработкии исключений на примере test_divide_and_conquer)

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



Темы урока:
- Unit тесты (на примере pytest)
- Покрытие тестов
- Многопоточный запуск тестов


[//]: # (TODO проверка на ноборе параметров test_factorial и test_factorial_1)
[//]: # (TODO проверка на ноборе параметров с кастомными названиями тестова test_factorial_1)

Чтобы pytest высчитывал покрытие тестов и 
заставлял разработчиков держать его на нужном уровне:
```shell
poetry add pytest-cov --group test
```

Чтобы дальше было удобнее было запускать pytest, 
добавим настройки его запуска в **pyproject.toml**:
```toml
[tool.pytest.ini_options]
minversion = "8.0"
addopts = [
    "--strict",
    "--cov-branch",
    "--cov-report=term-missing:skip-covered",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-fail-under=10",
    "--cov=.",
]
```
С такими настройками будет использоваться минимум 8-я версия pytest (```minversion = "8.0"```).
Также в поле **addopts** указаны параметры, 
которые будут передаваться pytest при каждом запуске:
- ```--strict``` - 
Выдает ошибку если в конфигурации или в метках тестов есть ошибки.
- ```--cov-branch``` - 
Включает измерение покрытия ветвей (branch coverage) наряду с покрытием строк. 
Иными словами без этого параметра pytest будет проверять покрытие заходов в например условия, 
но не будет проверять что тест охватывает обе ветви условия 
(те. должны проверяться и if и else блоки условия).
- ```--cov-report=term-missing:skip-covered``` - 
Выводит в терминал отчёт о покрытии с указанием пропущенных строк, 
но скрывает файлы, где покрытие 100%.
- ```--cov-report=html``` - 
Создаёт HTML‑отчёт о покрытии в папке **htmlcov/** 
(внутри интерактивная страница с цветовой индикацией, где можно увидеть процент покрытия по каждому файлу).
- ```--cov-report=xml``` - 
Генерирует отчёт в формате coverage.xml (стандартный формат для CI/CD).
- ```--cov-fail-under=10``` - 
Если общее покрытие кода ниже 10%, pytest завершит работу с ошибкой 
(заставляет разработчиков держать высокий уровень покрытия кода).
- ```--cov=.``` - 
Указывает, для каких файлов измерять покрытие 
(поскольку стоит ".", то для всех в текущей папке, где запускается pytest).

Обычно процент необходимого покрытия кода тестами в проекте 
постепенно увеличивают по мере развития проекта (не уменьшают!).

[//]: # (TODO)

Отчет о том, какие строки не покрыты тестами:
```
Name                      Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------
src/config.py                 5      5      0      0     0%   1-12
src/main.py                  11     11      2      0     0%   1-20
src/route/math_funcs.py       6      6      0      0     0%   1-10
---------------------------------------------------------------------
TOTAL                        62     22     14      0    68%
```

[//]: # (TODO как посмотреть coverage отчет в сгенеренном html файле)

[//]: # (TODO конфигурация pytest в pyproject.tml)
[//]: # (TODO параметры старта pytest в Makefile)

[//]: # (TODO ускорение запуска с использованием всех ядер)
```shell
poetry add pytest-xdist --group test
```

[//]: # (TODO запуск тестов в определенном порядке)
```shell
poetry add pytest-ordering --group test
```

```python
import pytest
@pytest.mark.run(order=1)
```
