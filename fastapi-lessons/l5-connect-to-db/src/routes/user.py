from fastapi import APIRouter

router = APIRouter()


@router.get('/list')
async def get_users_list():
    pass
    # return users
