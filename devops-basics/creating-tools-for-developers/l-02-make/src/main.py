import uvicorn
from fastapi import FastAPI

BASE_ROUTE_PATH = "/api/v1"

app = FastAPI(
    openapi_url=f"/openapi.json",
    docs_url=f"/docs",
)


@app.get('/hello-world')
async def hello_world():
    return "Hi mam!"


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
