from fastapi.responses import PlainTextResponse
from fastapi.routing import APIRouter
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.config import APP_VERSION
from src.metrics.container.collector_container import RegistryContainer
from src.schema.app_info import AppInfo

router = APIRouter(prefix="/app-info")


@router.get("/versions")
async def get_app_info() -> AppInfo:
    return AppInfo(back_version=APP_VERSION)


@router.get("/metrics")
async def metrics() -> PlainTextResponse:
    """Prometheus metrics endpoint"""
    return PlainTextResponse(
        generate_latest(RegistryContainer.registry()),
        media_type=CONTENT_TYPE_LATEST
    )
