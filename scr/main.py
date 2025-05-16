from exchanges.manager import ExchangeManager
from redisClient.omManager import omManager
import asyncio

omm = omManager()
em = ExchangeManager()

async def setup():
    asyncio.gather(omm.setup(), em.setup())


asyncio.run(setup())