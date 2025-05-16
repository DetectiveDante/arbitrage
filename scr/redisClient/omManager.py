from dtypes import Market, Network, Currency
from aredis_om import Migrator
import asyncio
from logger import Log



class omManager:
    log     = Log('ModelManager')
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
        self.log.n('migrate Models...', 'SETUP')
        migrator = Migrator()
        await migrator.run()
        self.log.n('migrate Models done', 'SETUP')

    async def scan_all_models(self):
        self.log.n('scan Models...', 'SETUP')
        currencies, networks, markets = await asyncio.gather(*[self.currency.find().all(), self.network.find().all(), self.market.find().all()])
        self.log.n('scan Models done!', 'SETUP')
        self.log.n(f'found currencies: {len(currencies)}', 'SETUP')
        self.log.n(f'found networks: {len(networks)}', 'SETUP')
        self.log.n(f'found markets: {len(markets)}', 'SETUP')
        
        return currencies, networks, markets

    async def update(self, model_name, **field_values):
        self.models[model_name].init_update(**field_values)

    async def find_model(self, model, expression):
        return self.models[model].find(expression).first()

    async def find_models(self, model, expression):
        return self.models[model].find(expression).all()

