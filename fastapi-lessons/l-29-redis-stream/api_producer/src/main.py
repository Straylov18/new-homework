import asyncio
import json
import math
from time import time

import uvicorn
from fastapi import Depends, FastAPI

from src.adapter.redis import get_redis_connection
from src.config import settings

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)


@app.get('/produce/{stream_key}/{messages_number}')
async def publish_message(stream_key: str, message: str = '', messages_number: int = 1,
                          redis_session=Depends(get_redis_connection)) -> str:
    for i in range(messages_number):
        data = {
            'time': time(),
            'message': message,
            'number': i,
            'balbla': 'blablabla'
        }
        msg_id = await redis_session.xadd(
            stream_key,
            {'ts': time(), 'v': i, 'data': json.dumps(data)}
        )
        print(f'Producer sent {msg_id}')
        # asyncio.create_task(
        #     redis_session.xadd(
        #         stream_key,
        #         {'ts': time(), 'v': i, 'data': json.dumps(data)}
        #     )
        # )
    success_message = f'stream {stream_key} length: {await redis_session.xlen(stream_key)}'
    print(success_message)
    return success_message


@app.delete('/delete-messages/{stream_key}')
async def delete_messages(stream_key: str, redis_session=Depends(get_redis_connection)):
    s1 = await redis_session.xread(streams={stream_key: 0})
    for streams in s1:
        stream_name, messages = streams
        # удаляем все id из листа сообщений стрима
        for i in messages:
            await redis_session.xdel(stream_name, i[0])


@app.delete('/trim-messages/{stream_key}')
async def trim_messages(stream_key: str, redis_session=Depends(get_redis_connection)):
    t_start = math.floor(1000 * time())
    print(t_start)
    # await redis_session.xtrim(stream_key, maxlen=1000, approximate=True)
    await redis_session.execute_command('XTRIM', stream_key, 'MINID', f'{t_start}-0')


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
