import uvicorn
from fastapi import Depends, FastAPI

from src.adapter.redis import get_redis_connection
from src.config import settings

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)


@app.get('/publish/{channel}')
async def publish_message(channel: str, message: str, redis_session=Depends(get_redis_connection)) -> str:
    await redis_session.publish(channel, message)
    return f"Published: {message}"


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
