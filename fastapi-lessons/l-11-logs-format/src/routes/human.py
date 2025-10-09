from fastapi import APIRouter

router = APIRouter()

humans = [
    {
        'title': 'Джавани Джоржио'
    },
    {
        'title': 'Иосиф Шпак'
    }
]


@router.get('/list')
async def get_humans_list():
    return humans


@router.get('/{human_position}')
async def get_human(human_position: int):
    return humans[human_position]
