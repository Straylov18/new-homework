import asyncio
import time

from adapter.redis import get_redis_connection
from config import settings


async def subscribe_channel():
    redis_session = await get_redis_connection()
    pubsub = redis_session.pubsub()
    await pubsub.subscribe(settings.CHANNEL_NAME)

    print(f'Subscribed to "{settings.CHANNEL_NAME}" channel.')

    while True:
        message = await pubsub.get_message()
        if message and not message['type'] == 'subscribe':
            print(f"Received: {message['data']}")
        time.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(subscribe_channel())
