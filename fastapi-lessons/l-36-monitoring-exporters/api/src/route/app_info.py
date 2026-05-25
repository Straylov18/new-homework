from fastapi.routing import APIRouter

from src.config import APP_VERSION
from src.schema.outputs import AppInfoOutput

router = APIRouter(prefix="/app-info")


@router.get("/versions")
async def get_app_info() -> AppInfoOutput:
    return AppInfoOutput(back_version=APP_VERSION)
