import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGIN]
)


@app.get('/some-endpoint')
def semo_func():
    return 'Some response!'


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
