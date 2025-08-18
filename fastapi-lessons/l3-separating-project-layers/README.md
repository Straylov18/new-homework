# Разделение backend приложения на слои

[//]: # (TODO зачем это делать и какие слои бывают)

## routes

Первое, что можно вынести в отдельный слой в приложении предыдущего урока это описание ручек.

Для этого создай папку routes и добавь в нее **__init__.py** файл, 
чтобы python считал эту папку своим пакетом. 
Для удобства можно выносить описание путей для каждой сущности в отдельный файл 
и импортировать router из его с отдельным префиксом в **main.py** файле.
Также можно будет добавить им свои теги, чтобы они разбивались по группам в openapi документации.

Например, пусть в приложении есть ручки для работы с сущностями людей и животных.
Тогда импортирование в **main.py** будет выглядеть следующим образом:
```python
from src.routes.animal import router as animal_router
from src.routes.human import router as human_router


router = APIRouter(prefix=settings.BASE_ROUTE_PATH)

router.include_router(animal_router, prefix='/animal', tags=['animal'])
router.include_router(human_router, prefix='/human', tags=['human'])

app.include_router(router)
```

Допустим в файле **src/routes/animal.py** описаны следующие ручки:
```python
from fastapi import APIRouter

router = APIRouter()

animals = [
    {
        'title': 'котик'
    },
    {
        'title': 'австралийский динго'
    }
]


@router.get('/list')
async def get_animals_list():
    return animals


@router.get('/{animal_position}')
async def get_animal(animal_position: int):
    return animals[animal_position]
```

Тогда итоговый путь по которому будет доступна ручка получения списка животных будет **/api/v1/animal/list**.
- /api/v1 (префикс из основного роутера в **main.py**)
- /animal (префикс добавляется при операции router.include_router роутера животных)
- /list (описание ручки)

## services

[//]: # (TODO)
