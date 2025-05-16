from .base import ExchangeBase
import asyncio

class Poloniex(ExchangeBase):
    def __init__(self, id):
      super().__init__(id)

    async def fetch_currencies(self, exchange):
      currenciesOut           = {}
      currencies, responseV2  = await asyncio.gather(*[exchange.fetch_currencies(), exchange.publicGetV2Currencies({'includeMultiChainCurrencies': True})])
      currencies2             = {k.get('coin'):k for k in responseV2}
      networks2               = {k.get('id'):k for currency2 in responseV2 for k in currency2.get('networkList')}
      for curr_id, curr_data in currencies.items():
        currency2 = currencies2.get(curr_id)

        if currency2 != None and not currency2.get('delisted'):
          curr_data['v2'] = currency2
          networks = {}
          for net_id, net_data in curr_data['networks'].items():
            network2 = networks2.get(str(net_data.get('numericId')))

            if network2 != None:
              if network2.get('contractAddress')!=None:
                networks[net_id] = net_data
                for key, value in net_data.items():
                  match key:
                    case 'deposit':
                      if value == None:
                        value = network2.get('depositEnable')

                    case 'withdraw':
                      if value == None:
                        value = network2.get('withdrawalEnable')

                    case 'precision':
                        if value == None:
                          if network2.get('decimals')!=None:
                            value = self.decimals_to_precision(int(network2.get('decimals')))

                    case 'fee':
                        if value == None:
                          if network2.get('withdrawFee')!=None:
                            value = float(network2.get('withdrawFee'))

                    case 'limits':
                      if value['withdraw'].get('min')==None:
                        if network2.get('withdrawMin') not in [None, '-1']:
                          value['withdraw']['min'] = network2.get('withdrawMin')

                  networks[net_id][key]=value
                networks[net_id]['contractAddress']  = network2['contractAddress']
                networks[net_id]['blockchain']      = network2['blockchain']
                networks[net_id]['v2']              = network2
             
          curr_data['networks'] = networks
          currenciesOut[curr_id] = curr_data

      return currenciesOut

    async def print_fetches(self):
      import pandas as pd

      currencies, markets, tradeFees, transferFees = await self.fetch_model_data()

      for key, i in {'currency':currencies['USDT'], 'network':currencies['USDT']['networks']['ERC20'], 'markets':markets['BTC/USDT'], 'transfer fee':transferFees['USDT'], 'trade fees':tradeFees['BTC/USDT']}.items():
        print('------------------------------------------------------------ ',key)
        info = i.get('info')
        i.pop('info')
        
        if key == 'network':
           v2 = i.get('v2')
           i.pop('v2')
           i.update(**{f'v2_{k}':v for k,v in v2.items()})
           #i.update(**{f'v2_info_{key}':v for k,v in v2info.items()})

        if type(info)==list:
          info = info[0]

        i.update(**{f'info_{k}':v for k,v in info.items()})
        print(pd.Series(i).to_markdown())

    async def fetch_model_data(self):
      exchange  = self.get_exchange()

      currencies, markets, tradeFees, transferFees = await asyncio.gather(*[
         self.fetch_currencies(exchange), 
         self.fetch_markets(exchange),
         self.fetch_trading_fees(exchange),
         self.fetch_transfer_fees(exchange)
         ])
      await exchange.close()

      return currencies, markets, tradeFees, transferFees

    async def get_model_data(self):
      currencies, markets, tradeFees, transferFees = await self.fetch_data()

      for currency_id, currency_info in currencies.items():
        networks = currency_info['networks']
        currency_info.pop('networks')

        if currency_id not in self.tradeSymbols['currencies']:
           continue

        self.currencies[currency_id]=self.parse_currency(
          self.id, 
          currency_info.get("code"), 
          currency_info.get('id'), 
          currency_info.get('deposit'), 
          currency_info.get('withdraw'), 
          currency_info.get('active'), 
          currency_info,
          list(networks.keys())
          )

        for network_id, network_data in networks.items():
          if transferFees[currency_id]['networks'].get(network_data.get('network')):
            self.networks[network_id] = self.parse_network(
                self.id, 
                currency_id, 
                network_data.get('withdraw'), 
                network_data.get('deposit'), 
                network_data.get('active'),
                network_data.get('precision'),
                fees={
                  'withdraw':transferFees[currency_id]['networks'][network_data.get('network')]['withdraw'],
                  'deposit':transferFees[currency_id]['networks'][network_data.get('network')]['deposit']
                },
                limits={k:v for k,v in network_data['limits'].items() if k != 'amount'},
                names=[network_data.get(i) for i in ['network', 'id', 'blockchain'] if network_data.get(i) != None],
                contractAddress=network_data.get('contractAddress'),
                info=network_data
                )

      for market_id, market in markets.items():
        self.markets[market_id] = self.parse_market(
          exchange =  self.id,
          id =        market_id,
          base =      market.get('base'),
          quote =     market.get('quote'),
          spot =      market.get('spot'),
          swap =      market.get('swap'),
          active =    market.get('active'),
          precision = market.get('precision'),
          limits =    market.get('limits'),
          fees =      tradeFees.get(market_id),
          info =      market
        )

      return dict(currencies=self.currencies, markets=self.markets, networks=self.networks)

    @classmethod
    async def setup(cls):
        instance:Poloniex = cls('poloniex')
        instance.log.n('initiating...', 'SETUP')
        await instance.ainit()
        instance.log.n('initiating done!', 'SETUP')
        return instance






"""def print_exchange_info():
    async def mainp():
        poloniex = await Poloniex.setup()
        from dell import printdict
        exchange = poloniex.get_exchange()
        
        c1= await exchange.fetch_currencies()
        c1=c1.get('BTC')
        c1['info']=c1['info'][0]
        c2=[i for i in await exchange.publicGetV2Currencies({'includeMultiChainCurrencies': True}) if i.get('coin')=='BTC'][0]
        n1=c1.get('networks')
        n2=c2.get('networkList')[0]
        c1.pop('networks')
        c2.pop('networkList')
        m = [i for i in await exchange.fetch_markets() if i.get('symbol')=='BTC/USDT'][0]
        exchange.close()
        for i in [c1,c2,n1,n2,m]:
            printdict(i)
            print('--------------------------------------------------------')

    asyncio.run(mainp())"""













# -------------------------------------------------------- FETCH CURRENCIES 
"""
   id                      BTC
   code                    BTC
   name                    Bitcoin
   active                  True
   deposit                 True
   withdraw                True
   fee                     0.001
   precision               None
   info
     BTC
       id                      28
       name                    Bitcoin
       description             BTC Clone
       type                    address
       withdrawalFee           0.00100000
       minConf                 2
       depositAddress          None
       blockchain              BTC
       delisted                False
       tradingState            NORMAL
       walletState             ENABLED
       walletDepositState      ENABLED
       walletWithdrawalState   ENABLED
       supportCollateral       True
       supportBorrow           True
       parentChain             None
       isMultiChain            True
       isChildChain            False
       childChains             ['BTCB', 'BTCTRON', 'WBTCETH']
   limits
     amount
       min                     None
       max                     None
     deposit
       min                     None
       max                     None
     withdraw
       min                     None
       max                     None
"""
# --------------------------------------------------------  FETCH PUBLIC V2 CURRENCIES
"""
   id                      28
   coin                    BTC
   delisted                False
   tradeEnable             True
   name                    Bitcoin
   supportCollateral       True
   supportBorrow           True
"""
# -------------------------------------------------------- FETCH CURRENCIES NETWORKS
"""
   BTC
     info
       id                      28
       name                    Bitcoin
       description             BTC Clone
       type                    address
       withdrawalFee           0.00100000
       minConf                 2
       depositAddress          None
       blockchain              BTC
       delisted                False
       tradingState            NORMAL
       walletState             ENABLED
       walletDepositState      ENABLED
       walletWithdrawalState   ENABLED
       supportCollateral       True
       supportBorrow           True
       parentChain             None
       isMultiChain            True
       isChildChain            False
       childChains             ['BTCB', 'BTCTRON', 'WBTCETH']
     id                      BTC
     network                 BTC
     currencyId              BTC
     numericId               28
     deposit                 True
     withdraw                True
     active                  True
     fee                     0.001
     precision               None
     limits
       amount                  {'min': None, 'max': None}
       withdraw                {'min': None, 'max': None}
       deposit                 {'min': None, 'max': None}
"""
#-------------------------------------------------------- FETCH PUBLIC V2 CURRENCIES NETWORKS
"""
   id                      581
   coin                    BTCB
   name                    Binance smart chain
   currencyType            address
   blockchain              BSC
   withdrawalEnable        False
   depositEnable           False
   depositAddress          None
   withdrawMin             -1
   decimals                8
   withdrawFee             0.00003000
   minConfirm              15
   contractAddress         0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c
"""
#-------------------------------------------------------- FETCH_MARKET
"""
   id                      BTC_USDT
   symbol                  BTC/USDT
   base                    BTC
   quote                   USDT
   settle                  None
   baseId                  BTC
   quoteId                 USDT
   settleId                None
   type                    spot
   spot                    True
   margin                  False
   swap                    False
   future                  False
   option                  False
   active                  True
   contract                False
   linear                  None
   inverse                 None
   contractSize            None
   expiry                  None
   expiryDatetime          None
   strike                  None
   optionType              None
   created                 1659018819512
   precision
     amount                  1e-06
     price                   0.01
   limits
     amount
       min                     1e-06
       max                     None
     price
       min                     None
       max                     None
     cost
       min                     1.0
       max                     None
   info
     symbol                  BTC_USDT
     baseCurrencyName        BTC
     quoteCurrencyName       USDT
     displayName             BTC/USDT
     state                   NORMAL
     visibleStartTime        1659018819512
     tradableStartTime       1659018819512
     symbolTradeLimit
       symbol                  BTC_USDT
       priceScale              2
       quantityScale           6
       amountScale             2
       minQuantity             0.000001
       minAmount               1
       maxQuantity             20
       maxAmount               2000000
       highestBid              0
       lowestAsk               0
     crossMargin
       supportCrossMargin      True
       maxLeverage             3
"""