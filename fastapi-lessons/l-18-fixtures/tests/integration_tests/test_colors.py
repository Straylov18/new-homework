import pytest


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
