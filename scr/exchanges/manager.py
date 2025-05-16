import asyncio
from custom.poloniex import Poloniex
from logger import get_logger
from typing import Dict

exchanges = [Poloniex]

class ExchangeManager:
    exchanges:Dict[str, Poloniex] = {}
    log = get_logger('Exchange Manager')

    async def ainit(self):
        self.log.info('start...', extra={'task':'SETUP'})
        self.exchanges = {v.id:v for v in await asyncio.gather(*[i.setup() for i in exchanges])}
        self.log.info('done!', extra={'task':'SETUP'})
    
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
                
