from fastapi import APIRouter, HTTPException

from src.scheme import User

router = APIRouter()

users = [User(email='qwe@mail.com', password='11')]


@router.post('/create-user')
async def create_user(body: User):
    for u in users:
        if u.email == body.email:
            raise HTTPException(status_code=400, detail="User with such email already exists!")
    users.append(body)
    return 'user created'


@router.post('/login')
async def login(body: User):
    for u in users:
        if u.email == body.email and u.password == body.password:
            return 'login succeeded'
    raise HTTPException(status_code=401, detail="Incorrect user name or password!")
