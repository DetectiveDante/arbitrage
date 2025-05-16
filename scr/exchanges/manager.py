import asyncio
from custom.poloniex import Poloniex
from logger import Log
from typing import Dict

exchanges = [Poloniex]

class ExchangeManager:
    exchanges:Dict[str, Poloniex] = {}
    
    def __init__(self):
        self.log = Log('Exchange Manager')
        self.log.n('start...', 'SETUP')
        self.log.n('done!', 'SETUP')

    async def ainit(self):
        coros = []
        for i in exchanges:
            coros.append(i.setup())

        for i in await asyncio.gather(*coros):
            self.exchanges[i.id]=i
    
    async def get_base_data(self):
        await asyncio.gather(*[exchange.get_model_data() for exchange in self.exchanges.values()])

    async def auto_fetch_base_data(self):
        while True:
            coros = []
            for exchange in self.exchanges.values():
                coros.append(exchange.get_model_data())
            
            model_data=dict(zip(self.exchanges.keys(), await asyncio.gather(*coros)))
            
            coros = []
            for exch_id, modeldata in model_data.items():
                for key, list_model_dicts in modeldata.items():
                    for dict in list_model_dicts:
                        coros.append(self.models.update(key, **dict))

            await asyncio.gather(*coros)
                
