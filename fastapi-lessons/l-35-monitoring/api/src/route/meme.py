from fastapi.routing import APIRouter

router = APIRouter(prefix="/memes")

memes = [
    'https://i.pinimg.com/736x/4d/3a/c8/4d3ac858664780a563373eccbfe2f2df.jpg',
    'https://i.pinimg.com/736x/16/44/ac/1644ac7494ef5e807dc1c86622288fe0.jpg',
    'https://cdn-edge.kwork.ru/pics/t3/29/26367851-642fd7620eb0c.jpg'
]


@router.get('/{id}',
            response_model=str)
async def get_meme(id: int) -> str:
    return memes[id]
