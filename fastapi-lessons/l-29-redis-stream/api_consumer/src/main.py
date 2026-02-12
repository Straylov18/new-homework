import asyncio
import json
import time

from redis.exceptions import ResponseError

from adapter.redis import get_redis_connection
from config import settings


async def consume_messages():
    redis_session = await get_redis_connection()

    # Create consumer group
    try:
        await redis_session.xgroup_create(
            settings.STREAM_KEY,
            settings.GROUP_NAME, '$',
            mkstream=True
        )
    except ResponseError as e:
        print(f'raised: {e}')  # Already exists

    print('Consumer waiting for messages...')

    while True:
        messages = await redis_session.xreadgroup(
            settings.GROUP_NAME,
            settings.CONSUMER_NAME,
            streams={settings.STREAM_KEY: '>'},
            count=1,
            block=1000
        )

        if not messages:
            continue

        for stream, msg_list in messages:
            for msg_id, fields in msg_list:
                data = json.loads(fields['data'])
                print(f'Consumer received: {msg_id} -> {data}')
                await redis_session.xack(settings.STREAM_KEY, settings.GROUP_NAME, msg_id)
                # asyncio.create_task(
                #     redis_session.xack(settings.STREAM_KEY, settings.GROUP_NAME, msg_id)
                # )

    await redis_session.close()


if __name__ == '__main__':
    asyncio.run(consume_messages())
