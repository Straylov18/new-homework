from pydantic import UUID4

from src.exception.common import NotFoundException
from src.repository.helicopter import HelicopterRepository
from src.schema.helicopter import DBHelicopter, HelicopterRegistration
from src.schema.outputs import HelicopterOutput


class HelicopterService:
    helicopter_repository: HelicopterRepository = HelicopterRepository()

    @classmethod
    async def get_by_uid(cls, uid: UUID4) -> HelicopterOutput:
        output = await cls.helicopter_repository.get_one(uid=uid)
        if output is None:
            raise NotFoundException()
        return HelicopterOutput(**output.__dict__)

    @classmethod
    async def create(cls, body: HelicopterRegistration) -> HelicopterOutput:
        output = await cls.helicopter_repository.add_one(
            data=body.model_dump(exclude_unset=True)
        )
        return HelicopterOutput(**output.__dict__)

    @classmethod
    async def update(cls, uid: UUID4, body: DBHelicopter) -> HelicopterOutput:
        await cls.get_by_uid(uid)  # to check if it exists
        output = await cls.helicopter_repository.update_one(
            uid=uid,
            update_data=body.model_dump(exclude_unset=True)
        )
        return HelicopterOutput(**output.__dict__)

    @classmethod
    async def delete(cls, uid: UUID4) -> HelicopterOutput:
        helicopter: HelicopterOutput = await cls.get_by_uid(uid)  # to check if it exists
        await cls.helicopter_repository.delete_one(uid=uid)
        return helicopter
