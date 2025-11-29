import pytest


@pytest.fixture
def red_color_params():
    return {'r': 100, 'g': 2, 'b': 3}


@pytest.fixture
def green_color_params():
    return {'r': 1, 'g': 200, 'b': 3}


@pytest.fixture
def blue_color_params():
    return {'r': 1, 'g': 2, 'b': 300}
