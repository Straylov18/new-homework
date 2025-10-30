from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, desc

from src.schemes.user import UserCreate, UserFromDB, Filters
from src.models.user import User
from src.db.session import engine, get_session

router = APIRouter()


@router.post('/list')
async def get_users_list(filters: Filters, db_session: AsyncSession = Depends(get_session)) -> list[UserFromDB]:
    query = select(User)
    if filters.search_str is not None:
        query = query.filter(
            or_(
                User.name.ilike(f"%{filters.search_str}%"),
                User.email.ilike(f"%{filters.search_str}%"),
            )
        )
    if filters.date_created__gte is not None:
        query = query.filter(User.date_created >= filters.date_created__gte)
    if filters.date_created__lte is not None:
        query = query.filter(User.date_created <= filters.date_created__lte)
    if filters.email__in is not None:
        query = query.filter(User.email.in_(filters.email__in))
    if filters.order_by is not None:
        # query = query.order_by(desc("name"), "email")
        if filters.order_desc:
            query = query.order_by(desc(filters.order_by))
        else:
            query = query.order_by(filters.order_by)
    if filters.limit is not None and filters.limit >= 0:
        query = query.limit(filters.limit)
    if filters.offset is not None:
        query = query.offset(filters.offset)

    query_result = await db_session.execute(query)
    return query_result.scalars().all()


@router.post('/')
async def create_user(body: UserCreate, db_session: AsyncSession = Depends(get_session)) -> UserFromDB:
    new_user = User(name=body.name, email=body.email)
    db_session.add(new_user)
    await db_session.commit()
    return new_user
