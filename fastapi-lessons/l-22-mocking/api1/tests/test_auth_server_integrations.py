import pytest
from httpx import ASGITransport, AsyncClient

from src.config import settings
from src.main import app

async_client = AsyncClient(
    transport=ASGITransport(app=app),
    base_url='http://test'
)


@pytest.mark.asyncio
async def test_login_counter(mocker):
    async with async_client as ac:
        mock_login = mocker.patch('src.service.some_service.httpx.post')
        mock_login.return_value.json.return_value = 'login succeeded'

        response = await ac.post('/api/v1/some-router/login', json={'email': '1', 'password': '1'})
        mock_login.assert_called_once_with(
            f'{settings.AUTH_SERVER_ADDRESS}/user/login',
            json={'email': '1', 'password': '1'}
        )
        assert response.json() == 'Залогинились через отдельностоящий сервис'
        assert response.status_code == 200

        mock_login = mocker.patch('src.service.some_service.httpx.post')
        mock_login.return_value.json.return_value = 'login NOT succeeded (be-be he-he)'

        response = await ac.post('/api/v1/some-router/login', json={'email': '2', 'password': '2'})
        mock_login.assert_called_once_with(
            f'{settings.AUTH_SERVER_ADDRESS}/user/login',
            json={'email': '2', 'password': '2'}
        )
        assert response.json() == {'detail': 'Не получилось войти через отдельностоящий сервис!'}
        assert response.status_code == 400

        response = await ac.get('/api/v1/some-router/list-successful-logins')
        assert response.json() == [{'email': '1', 'password': '1'}]
        assert response.status_code == 200
