import pytest

from src.service.math_funcs import get_dominant_color


# @pytest.mark.run(order=1)
def test_colors():
    assert get_dominant_color(100, 100, 100) == 'same'
    assert get_dominant_color(0, 100, 100) == 'green, blue'
    assert get_dominant_color(100, 10, 100) == 'red, blue'
    assert get_dominant_color(0, 10, 100) == 'blue'
    assert get_dominant_color(0, 100, 0) == 'green'
    assert get_dominant_color(101, 100, 100) == 'red'
