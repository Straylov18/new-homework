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
