# Парсинг api существующих сайтов

## Отправка REST запросов с помощью библиотеки requests

Для начала установим библиотеку requests:
```shell
pip install requests
```

[//]: # (TODO что за сервис который парсится здесь)

```python
import requests

url = 'https://api.data.gov/ed/collegescorecard/v1/schools?api_key=DEMO_KEY&fields=id%2Cname%2Clocation%2Cstudent.size'

response = requests.get(url)

print(response.status_code)
print(response.json())
```
Здесь:
- ```requests.get(url)``` отправляет REST запрос типа GET (аналогично можно отправлять все виды REST запросов ```requests.post(url)```, ```requests.patch(url)```, ...)
- ```response.status_code``` возвращает код ответа запроса
- ```response.json()``` возвращает тело ответа, конвертированное в словарь 

Чтобы выводить значения в красивом формате добавим отступы к выводимому json:
```python
import json

# ... тут код самого запроса ...

print(json.dumps(response.json(), indent=4))
```

[//]: # (TODO как парсить инфу с сайтов)
