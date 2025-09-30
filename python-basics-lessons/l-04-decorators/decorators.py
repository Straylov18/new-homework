def some_decorator(func):
    def wrapper():
        print('выводиться перед вызовом функции')
        func()
        print('выводиться после вызова функции')

    return wrapper


@some_decorator
def some_func_1():
    print('some_func_1')


@some_decorator
def some_func_2():
    print('some_func_2')


some_func_1()  # выведет текст из комментариев ниже:
# выводиться перед вызовом функции
# some_func_1
# выводиться после вызова функции
some_func_2()  # выведет текст из комментариев ниже:
# выводиться перед вызовом функции
# some_func_2
# выводиться после вызова функции


# Декораторы с доп параметрами:
print('--- Декораторы с доп параметрами ---')


def hello_decorator(n):
    def actual_decorator(func):
        def wrapper():
            for i in range(n+1):
                print('выводиться перед вызовом функции')
            result = func()  # вызов оригинальной функции
            return result
        return wrapper
    return actual_decorator


@hello_decorator(3)
def some_func_3():
    print('some_func_3')


@hello_decorator(2)
def some_func_4():
    print('some_func_4')


some_func_3()  # выведет текст из комментариев ниже:
# выводиться перед вызовом функции
# выводиться перед вызовом функции
# выводиться перед вызовом функции
# выводиться перед вызовом функции
# some_func_3
some_func_4()  # выведет текст из комментариев ниже:
# выводиться перед вызовом функции
# выводиться перед вызовом функции
# some_func_4
