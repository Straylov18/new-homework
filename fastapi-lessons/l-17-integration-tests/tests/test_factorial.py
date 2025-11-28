import pytest
import math

from src.main import app

from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.mark.parametrize("number", [0, 1, 2, 3, 100])
def test_factorial_using_std_lib(number):
    response = client.get('/api/v1/math/factorial', params={'n': number})
    assert response.json() == math.factorial(number)
    assert response.status_code == 200


@pytest.mark.parametrize("number, factorial_result", [
    (0, 1),
    (1, 1),
    (2, 2),
    (3, 6),
    (25, 15511210043330985984000000),
    # (arg1_value, arg2_value),
    # ...
], ids=["проверка 0", "проверка 1", "проверка 2", "проверка 3", "проверка очень большого числа"])
def test_factorial_using_precalculated_values(number, factorial_result):
    response = client.get('/api/v1/math/factorial', params={'n': number})
    assert response.json() == factorial_result
    assert response.status_code == 200
