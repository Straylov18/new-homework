import uvicorn
from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.routing import APIRouter

from src.config import settings

print(f'using base prefix: {settings.BASE_ROUTE_PATH}')

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)


def get_file_path(filename: str) -> str:
    return f"{settings.FILES_DIR}/{filename}"


@router.post('/upload_file')
async def upload_file(upload_file: UploadFile):
    file = upload_file.file
    filename = upload_file.filename
    with open(get_file_path(filename), "wb") as f:
        f.write(file.read())
    return "File uploaded"


@router.post('/upload_multiple_file')
async def upload_multiple_file(upload_files_list: list[UploadFile]):
    for upload_file in upload_files_list:
        file = upload_file.file
        filename = upload_file.filename
        with open(get_file_path(filename), "wb") as f:
            f.write(file.read())
        return "File uploaded"


@router.get('/file/{filename}')
async def get_file(filename: str) -> FileResponse:
    return FileResponse(get_file_path(filename))


def iterate_file(filename: str):
    with open(get_file_path(filename), "rb") as f:
        while file_chunk := f.read(1024 * 1024):
            yield file_chunk


def get_filename_media_type(filename: str) -> str:
    file_extension = filename.split('.')[-1]
    if file_extension == '.txt':
        return 'text/txt'
    elif file_extension == '.html':
        return 'text/html'
    elif file_extension == '.png':
        return 'image/mp4'
    elif file_extension == '.jpeg':
        return 'image/jpg'
    elif file_extension == '.gif':
        return 'image/gif'
    elif file_extension == '.mp4':
        return 'video/mp4'
    elif file_extension == '.mpeg':
        return 'video/mpeg'


@router.get('/file-streaming/{filename}')
async def get_file_streaming(filename: str) -> StreamingResponse:
    return StreamingResponse(
        iterate_file(filename),
        media_type=get_filename_media_type(filename)
    )


app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
