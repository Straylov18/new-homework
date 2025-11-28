import pytest

from src.main import app

from fastapi.testclient import TestClient

client = TestClient(app)


def test_divide_and_conquer():
    response = client.get('/api/v1/math/divide_and_conquer',
                          params={'num': 8, 'denum': 4})
    assert response.json() == "conquered 2 times"
    assert response.status_code == 200

    response = client.get('/api/v1/math/divide_and_conquer',
                          params={'num': 12, 'denum': 2})
    assert response.json() == "conquered 6 times"
    assert response.status_code == 200


def test_divide_and_conquer_exception():
    with pytest.raises(Exception, match="denum must not be 0!"):
        response = client.get('/api/v1/math/divide_and_conquer',
                              params={'num': 5, 'denum': 0})
        assert response.json() == "denum must not be 0!"
        assert response.status_code == 500
