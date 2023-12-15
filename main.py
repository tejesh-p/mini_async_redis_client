import asyncio

from client import RedisClient


async def runner(client):
    for _ in range(1000):
        await client.send("incr", "banana")


async def main():
    client = RedisClient()
    await client.connect("localhost", 6379)

    asyncio.create_task(runner(client))
    asyncio.create_task(runner(client))
    asyncio.create_task(runner(client))

    await asyncio.sleep(10)


if __name__ == "__main__":
    # Note: uncomment this if you are on windows
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
