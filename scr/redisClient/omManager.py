from dtypes import Market, Network, Currency
from aredis_om import Migrator
import asyncio
from logger import get_logger



class omManager:
    log     = get_logger('ModelManager')
    market  = Market
    network = Network
    currency= Currency

    @classmethod
    async def ainit(self):
        await self._migrate_models()
        await self.scan_all_models()
        
    def get_modeltype(self, key):
        self.__dict__.get(key)

    async def _migrate_models(self):
        self.log.info('started...', extra={'task':'migrate models'})
        migrator = Migrator()
        await migrator.run()
        self.log.info('done', extra={'task':'migrate models'})

    async def scan_all_models(self):
        self.log.info('started...', extra={'task':'scan models'})
        currencies, networks, markets = await asyncio.gather(*[self.currency.find().all(), self.network.find().all(), self.market.find().all()])
        self.log.info('scan Models done!', 'SETUP')
        self.log.info(f'found currencies: {len(currencies)}', extra={'task':'scan models'})
        self.log.info(f'found networks: {len(networks)}', extra={'task':'scan models'})
        self.log.info(f'found markets: {len(markets)}', extra={'task':'scan models'})
        
        return currencies, networks, markets

    async def update(self, model_name, **field_values):
        self.get_modeltype(model_name).init_update(**field_values)

    async def find_model(self, model_name, expression):
        return self.get_modeltype(model_name).find(expression).first()

    async def find_models(self, model_name, expression):
        return self.get_modeltype(model_name).find(expression).all()

