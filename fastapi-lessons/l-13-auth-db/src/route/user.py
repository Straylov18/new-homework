from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapter.db.session import get_session
from src.scheme.user import UserFromDB
from src.service.user import UserService

router = APIRouter()


@router.get('/list')
async def get_users_list(db_session: AsyncSession = Depends(get_session)) -> list[UserFromDB]:
    return [u.serialize() for u in await UserService.get_users_list(db_session)]
