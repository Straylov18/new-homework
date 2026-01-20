sqr = lambda x: x * x
print(sqr(5))  # выведет 25

# несколько переменных в лямбда функциях
add = lambda a, b: a + b
print(add(3, 7))  # выведет 10

# условия в лямбда функциях
max_num = lambda a, b: a if a > b else b
print(max_num(10, 5))  # выведет 10

# передача лямбда функции в качестве параметра
numbers = [1, 2, 3, 4]
doubled = list(map(lambda x: x * 2, numbers))
print(doubled)  # выведет [2, 4, 6, 8]

numbers = [1, 2, 3, 4, 5, 6]
even = list(filter(lambda x: x % 2 == 0, numbers))
print(even)  # выведет [2, 4, 6]

words = ['11', 'qweqwe', 'e']
sorted_words = sorted(words, key=lambda x: len(x))
print(sorted_words)  # выведет ['e', '11', 'qweqwe'] (отсортированные по длине)

from functools import reduce
numbers = [1, 2, 3, 4]
product = reduce(lambda x, y: x * y, numbers)
print(product)  # выведет 24 (1*2*3*4 = 24)
