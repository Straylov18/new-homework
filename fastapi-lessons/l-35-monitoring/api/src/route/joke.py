from fastapi.routing import APIRouter

router = APIRouter(prefix="/joke")

jokes = [
    'Колобок повесился.',
    'Из окна дуло, Штирлец закрыл окно и дуло исчезло.',
    'Штирлицу в голову попала пуля. "Разрывная" - подумал Штирлец, широко пораскинув мозгами.'
]


@router.get('/{id}',
            response_model=str)
async def get_joke(id: int) -> str:
    return jokes[id]
