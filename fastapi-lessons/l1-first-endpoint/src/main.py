import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

BASE_ROUTE_PATH = "/api/v1"

app = FastAPI(
    openapi_url=f"{BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{BASE_ROUTE_PATH}/docs",
)

router = APIRouter(prefix=BASE_ROUTE_PATH)

objects = [
    {
        'id': 0,
        'title': 'Штаны'
    },
    {
        'id': 1,
        'title': 'Перфоратор'
    },
    {
        'id': 2,
        'title': 'Леденец "петушок"'
    },
    {
        'id': 3,
        'title': 'Клюшка для гольфа'
    },
]


@router.get('/object/{object_id}')
async def get_object(object_id):
    # TODO check if None
    return next((o for o in objects if o['id'] == object_id), None)


@router.get('/object/list')
async def get_objects_list(limit: int = -1, offset: int = 0):
    # Здесь возвращается слайс листа объектов (копия листа, состоящая из части элементов первоначального листа)
    # Они указываются следующим образом list[start:stop] или list[start:stop:step]
    #   start - номер начального элемента (включительно)
    #   stop - номер финального элемента (не включительно)
    #   step - шаг, с которым выбираются элементы (по умолчанию 1)
    # Если при взятии слайса ты не указываешь какой-то параметр,
    # то python будет использовать для него значение по умолчанию:
    #   start по умолчанию равен 0
    #   stop по умолчанию равен длинеисходного массива
    #   step по умолчанию равен 1
    if limit == -1:
        # если limit равен -1, то возвращаются все объекты начиная с объекта, лежащего под номером offset
        return objects[offset:]
    else:
        # если лимит положительный, то возвращается объктов не больше, чем значение limit
        return objects[offset:offset+limit]


@router.post('/object/create')
async def create_object(new_object: dict):
    objects.append(new_object)
    # возвращается последний элемент листа (который мы только что добавили)
    return objects[-1]


# @router.put('/product/put')
# async def put_object(new_object: dict):
#     objects.append(new_product)
#     return "product created"
#
#
# @router.patch('/product/create')
# async def patch_object(new_object: dict):
#     objects.append(new_product)
#     return "product created"


app.include_router(router)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        access_log=False,
        port=8000,
        reload=True,
    )
