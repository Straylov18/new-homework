import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def async_client():
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    )


@pytest.fixture
def user_data_1():
    return {'email': 'first@mail.com', 'password': '1'}


@pytest.fixture
def user_data_2():
    return {'email': 'second@mail.com', 'password': '22'}


@pytest.fixture
def clear_login_logs(client):
    client.delete('/api/v1/some-router/clear-login-logs')
