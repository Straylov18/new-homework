from src.schemes.user import UserCreate, UserWithId

users = [
    {
        "id": 0,
        "name": "Иоан Веселый",
        "email": "io.an@gay.ua"
    },
    {
        "id": 1,
        "name": "Иоан Веселый",
        "email": "io.an@gay.ua"
    }
]


class UserService:
    def _convert_dict_to_pydantic_scheme(user: dict) -> UserWithId:
        output = UserWithId(id=user['id'], name=user['name'], email=user['email'])
        return output

    def get_users_list() -> list[UserWithId]:
        return [UserService._convert_dict_to_pydantic_scheme(u) for u in users]

    def create_user(user: UserCreate) -> UserWithId:
        users.append({
            "id": len(users),
            "name": user.name,
            "email": user.email
        })
        return users[-1]
