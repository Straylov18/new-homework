import pytest

from src.main import app

# ---- not async ----

from fastapi.testclient import TestClient

client = TestClient(app)

def test_compare_colors():
    response = client.get('/api/v1/math/compare-colors', params={'r': 1, 'g': 2, 'b': 300})
    assert response.json() == 'blue'
    assert response.status_code == 200

# ---- async ----
# если нужно протестировать асинхронную работу приложения

from httpx import AsyncClient, ASGITransport

async_client = AsyncClient(
    transport=ASGITransport(app=app),
    base_url='http://test'
)

@pytest.mark.asyncio  # чтобы тест вызывался асинхронно
async def test_compare_colors_async():
    async with async_client as ac:
        response = await ac.get('/api/v1/math/compare-colors', params={'r': 1, 'g': 2, 'b': 300})
        assert response.json() == 'blue'
        assert response.status_code == 200
