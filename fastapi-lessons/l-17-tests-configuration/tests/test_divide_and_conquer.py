import pytest

from src.service.math_funcs import divide_and_conquer


def test_divide_and_conquer():
    assert divide_and_conquer(8, 4) == "conquered 2 times"
    assert divide_and_conquer(12, 2) == "conquered 6 times"


def test_divide_and_conquer_exception():
    with pytest.raises(Exception, match="denum must not be 0!"):
        divide_and_conquer(5, 0)
