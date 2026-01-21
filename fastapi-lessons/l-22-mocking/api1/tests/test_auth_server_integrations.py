import pytest

from src.config import settings


@pytest.mark.asyncio
async def test_login_succeeded(mocker, async_client, user_data_1):
    async with async_client as ac:
        mock_login = mocker.patch('src.service.some_service.httpx.post')
        mock_login.return_value.json.return_value = 'login succeeded'

        response = await ac.post('/api/v1/some-router/login', json=user_data_1)
        mock_login.assert_called_once_with(
            f'{settings.AUTH_SERVER_ADDRESS}/user/login',
            json=user_data_1
        )
        assert response.json() == 'Залогинились через отдельностоящий сервис'
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_login_failed(mocker, async_client, user_data_1):
    async with async_client as ac:
        mock_login = mocker.patch('src.service.some_service.httpx.post')
        mock_login.return_value.json.return_value = 'NOT succeeded (be-be he-he)'

        response = await ac.post('/api/v1/some-router/login', json=user_data_1)
        mock_login.assert_called_once_with(
            f'{settings.AUTH_SERVER_ADDRESS}/user/login',
            json=user_data_1
        )
        assert response.json() == {'detail': 'Не получилось войти через отдельностоящий сервис!'}
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_counter(mocker, async_client, clear_login_logs, user_data_1, user_data_2):
    async with async_client as ac:
        mock_login = mocker.patch('src.service.some_service.httpx.post')
        mock_login.return_value.json.return_value = 'login succeeded'

        await ac.post('/api/v1/some-router/login', json=user_data_1)
        await ac.post('/api/v1/some-router/login', json=user_data_2)

        mock_login = mocker.patch('src.service.some_service.httpx.post')
        mock_login.return_value.json.return_value = 'login NOT succeeded (be-be he-he)'

        # не должно записывать в логи, потому что мы замокировали ошибку
        await ac.post('/api/v1/some-router/login', json=user_data_2)

        response = await ac.get('/api/v1/some-router/list-successful-logins')
        assert response.json() == [user_data_1, user_data_2]
        assert response.status_code == 200
