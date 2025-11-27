import math

import pytest

from src.service.math_funcs import get_dominant_color, my_factorial


@pytest.mark.parametrize("number", [0, 1, 2, 3, 100])
def test_factorial(number):
    assert my_factorial(number) == math.factorial(number)


@pytest.mark.parametrize("number, factorial_result", [
    (0, 1),
    (1, 1),
    (2, 2),
    (3, 6),
    (25, 15511210043330985984000000),
    # (arg1_value, arg2_value),
    # ...
], ids=["проверка 0", "проверка 1", "проверка 2", "проверка 3", "проверка очень большого числа"])
def test_factorial_1(number, factorial_result):
    assert my_factorial(number) == factorial_result


# @pytest.mark.run(order=1)
def test_colors():
    assert get_dominant_color(100, 100, 100) == 'same'
    assert get_dominant_color(0, 100, 100) == 'green, blue'
    assert get_dominant_color(100, 10, 100) == 'red, blue'
    assert get_dominant_color(0, 10, 100) == 'blue'
    assert get_dominant_color(0, 100, 0) == 'green'
    assert get_dominant_color(101, 100, 100) == 'red'
