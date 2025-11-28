import math

import pytest

from src.service.math_funcs import my_factorial


@pytest.mark.parametrize("number", [0, 1, 2, 3, 100])
def test_factorial_using_std_lib(number):
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
def test_factorial_using_precalculated_values(number, factorial_result):
    assert my_factorial(number) == factorial_result
