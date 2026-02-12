import asyncio
import json
import time

from redis.exceptions import ResponseError

from adapter.redis import get_redis_connection
from config import settings


async def subscribe_channel():
    redis_session = await get_redis_connection()
    stream_key = settings.STREAM_KEY
    group_name = settings.GROUP_NAME
    consumer_name = settings.CONSUMER_NAME  # consumers with different names can read not delivered messages

    # Create consumer group
    try:
        await redis_session.xgroup_create(stream_key, group_name, '$', mkstream=True)
    except ResponseError as e:
        print(f'raised: {e}')  # Already exists

    print('Consumer waiting for messages...')

    while True:
        messages = await redis_session.xreadgroup(
            group_name, consumer_name,
            streams={stream_key: '>'},
            count=1,
            block=10
        )

        if not messages:
            continue

        for stream, msg_list in messages:
            for msg_id, fields in msg_list:
                data = json.loads(fields['data'])
                print(f'Consumer received: {msg_id} -> {data}')
                await redis_session.xack(stream_key, group_name, msg_id)
        time.sleep(0.1)

    await redis_session.close()


if __name__ == '__main__':
    asyncio.run(subscribe_channel())
