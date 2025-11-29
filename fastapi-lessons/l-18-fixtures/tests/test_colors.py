import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.fixture
def red_color_params():
    return {'r': 100, 'g': 2, 'b': 3}


@pytest.fixture
def green_color_params():
    return {'r': 1, 'g': 200, 'b': 3}


@pytest.fixture
def blue_color_params():
    return {'r': 1, 'g': 2, 'b': 300}


@pytest.fixture
def async_client():
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    )


@pytest.fixture
def before_colors_test():
    print("will be done before starting colors test")


@pytest.mark.usefixtures("before_colors_test")
class TestColors:
    @pytest.mark.asyncio
    async def test_compare_colors_red(self, async_client, red_color_params):
        async with async_client as ac:
            response = await ac.get('/api/v1/colors/compare-colors',
                                    params=red_color_params)
            assert response.json() == 'red'
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_compare_colors_green(self, async_client, green_color_params):
        async with async_client as ac:
            response = await ac.get('/api/v1/colors/compare-colors',
                                    params=green_color_params)
            assert response.json() == 'green'
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_compare_colors_blue(self, async_client, blue_color_params):
        async with async_client as ac:
            response = await ac.get('/api/v1/colors/compare-colors',
                                    params=blue_color_params)
            assert response.json() == 'blue'
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_compare_colors_list(self, async_client, red_color_params, green_color_params, blue_color_params):
        colors_list = [red_color_params, green_color_params, blue_color_params]
        async with async_client as ac:
            response = await ac.post('/api/v1/colors/compare-colors-list',
                                     json=colors_list)
            assert response.json() == ['red', 'green', 'blue']
            assert response.status_code == 200
