from fastapi import HTTPException
from fastapi.routing import APIRouter
from pydantic import UUID4

from src.exception.common import NotFoundException
from src.schema.helicopter import DBHelicopter, HelicopterRegistration
from src.schema.outputs import HelicopterOutput
from src.service.helicopter import HelicopterService

router = APIRouter(prefix="/helicopter")


@router.get("/get/{uid}")
async def get_helicopter(uid: UUID4) -> HelicopterOutput:
    try:
        return await HelicopterService.get_by_uid(uid)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Helicopter not found")


@router.post("/register")
async def register(body: HelicopterRegistration) -> HelicopterOutput:
    try:
        return await HelicopterService.create(body)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Helicopter not found")


@router.put("/update/{uid}")
async def update(uid: UUID4, body: DBHelicopter) -> HelicopterOutput:
    try:
        return await HelicopterService.update(uid, body)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Helicopter not found")


@router.delete("/delete/{uid}")
async def delete(uid: UUID4) -> HelicopterOutput:
    try:
        return await HelicopterService.delete(uid)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Helicopter not found")
