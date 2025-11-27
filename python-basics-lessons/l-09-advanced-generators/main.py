def some_generator():
    yield "1 значение"
    yield "2 значение"
    yield "3 значение"


gen1 = some_generator()
print(next(gen1))  # выдаст "1 значение"
print(next(gen1))  # выдаст "2 значение"
print(next(gen1))  # выдаст "3 значение"
# print(next(gen))  # выдаст ошибку если нечего больше выдавать
print(next(gen1, None))  # чтобы при окончании последовательности не появлялась ошибка, можно ставить значение по умолчанию у next

print("----some_generator через цикл for----")
gen2 = some_generator()
for i in gen2:  # for цикл под капотом как раз использует next метод до тех пор, пока не наткнется на StopIteration
    print(i)  # выдаст "1 значение", потом "2 значение", потом "3 значение"


def fibonacci_numbers(n: int):
    # def generator():
    last = 1
    before_last = 0
    for _ in range(n):
        yield last
        new_last = last + before_last
        before_last = last
        last = new_last
        # or just
        # yield last
        # last, before_last = last + before_last, last


print("----fibonacci_numbers----")
for fn in fibonacci_numbers(5):
    print(fn)

print("----генераторы в одну строчку----")
# короткое задание генератора
short_form_generators = (i * 2 for i in range(5))
for i in short_form_generators:
    print(i)
# выдаст 0 потом 2 потом 4 ... до 8

print("----конвертации генераторов----")
# перевод в лист
l = list(range(5))
print(l)  # выдаст [0, 1, 2, 3, 4]
# подсчет числа элементов последовательности
length = sum(1 for _ in range(5))
print(length)  # выдаст 5

print("----конвейеры (пайплайны) генераторов----")
# следующий код выполниться без сохранения промежуточных листов
range_gen = range(5)
minus_one_gen = (i - 1 for i in range_gen)
multiply_by_2_gen = (2 * i for i in minus_one_gen)
for i in multiply_by_2_gen:
    print(i)
# выдаст -2, 0, 2, 4, 6 (иными словами числа соответствующие формуле 2*(i-1))
