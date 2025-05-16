import ccxt.pro as ccxt
from logger import Log
import asyncio
from redisClient.asyncClient import get_api_info
from typing import List, Optional, Dict, Any

class ExchangeBase:
    def __init__(self, id):
        self.log            = Log(id)
        self.infos          = {}
        self.id:str         = id
        self.tradeSymbols   = {'currencies':[], 'markets':[]}
        self.currencies     = {}
        self.markets        = {}
        self.networks       = {}
        self.isApiWorking   = True
        self.exchange:      ccxt.Exchange = None
        self.has            = getattr(ccxt, self.id)().describe()['has']
        self.task_fetch_ticker={}
    
    async def ainit(self):
        self.info = await get_api_info(self.id)
        exchange = self.get_exchange()
        fetchedMarkets = await exchange.load_markets(True)
        await exchange.close()

        self.tradeSymbols['currencies'] = [v['base'] if v['base'] != 'USDT' else v['quote'] for k,v in fetchedMarkets.items() if 'USDT' in (v['base'],v['quote'])]+['USDT']
        self.tradeSymbols['markets']    = [k for k,v in fetchedMarkets.items() if v['base'] in self.tradeSymbols['currencies'] and v['quote']in self.tradeSymbols['currencies']]


    def parse_currency(self, exchange: str, id: str, symbol: str, deposit: bool = False,
                withdraw: bool = False, active: bool = False, info: dict = {}, networks: list = []):
        return {
            'exchange'  : exchange,
            'id'        : id,
            'symbol'    : symbol,
            'deposit'   : deposit,
            'withdraw'  : withdraw,
            'active'    : active,
            'info'      : info,
            'networks'  : networks
        }
    
    def parse_market(cls, exchange: str, id: str, base: str, quote: str, spot: bool, swap: bool,
                active: bool, precision: dict, limits: dict, fees: dict, info: Dict[str, Any]):
        return {
            'exchange': exchange,
            'id': id,
            'base': base,
            'quote': quote,
            'spot': spot,
            'swap': swap,
            'active': active,
            'precision': precision,
            'limits': limits,
            'fees': fees,
            'info': info
        }

    def parse_network(self, exchange: str, currency: str, withdraw: bool, deposit: bool, active: bool,
                precision: Optional[float], fees: dict, limits: dict, names: List[str],
                depositAddress: Optional[str] = None, contractAddress: Optional[str] = None,
                info: Dict[str, Any] = {}, id: Optional[str] = None):
        return {
            'exchange':         exchange,
            'currency':         currency,
            'withdraw':         withdraw,
            'deposit':          deposit,
            'active':           active,
            'precision':        precision,
            'fees':             fees,
            'limits':           limits,
            'names':            names,
            'depositAddress':   depositAddress,
            'contractAddress':  contractAddress,
            'info':             info,
            'id':               id
        }

    def fetch_tickers_forever(self):
        loop=asyncio.get_running_loop()
        if not loop:
            loop = asyncio.new_event_loop()
        asyncio.run_coroutine_threadsafe(self._update_tickers(), loop)

    """async def _update_tickers(self):
        exchange = self.get_exchange()
        self.log.n('auto fetching started', 'FETCH TICKERS')

        try:
            while True:
                coros = []
                markets, tickers = await asyncio.gather(*[Market.find(Market.exchange == self.id).all(), exchange.fetch_tickers(self.markets.keys())])

                for market in markets:
                    ticker = tickers.get(market.id)
                    coros.append(market.update_ticker(**{k:v for k,v in ticker.items() if k in ['timestamp', 'bid', 'ask', 'close']}))

                await asyncio.gather(*coros)
                break
            self.log.n('fetch done!', 'FETCH TICKERS', 'error')

        except Exception as e:
            self.log.n(f'{e}', 'FETCH TICKERS', 'error')

        finally:
            exchange.close()"""

    def decimals_to_precision(self, digit):
        if digit == 0:
            return 1.0
        else:
            return 1/(10*digit)
        
    async def fetch_transfer_fees(self, exchange:ccxt.bitget, symbols=None):
        if not symbols:
            symbols = self.tradeSymbols['currencies']

        if self.has.get('fetchDepositWithdrawFees'):
            return await exchange.fetch_deposit_withdraw_fees(symbols)
        
        elif self.has.get('fetchDepositWithdrawFee'):
            return dict(zip(symbols, await asyncio.gather(*[exchange.fetch_deposit_withdraw_fee(symbol) for symbol in symbols])))
    
    async def fetch_trading_fees(self, exchange:ccxt.bitget, symbols=None):
        if not symbols:
            symbols = self.tradeSymbols['markets']

        if self.has.get('fetchTradingFees'):
            return await exchange.fetch_trading_fees()
        
        elif self.has.get('fetchTradingFee'):
            return dict(zip(symbols, await asyncio.gather(*[exchange.fetch_trading_fee(symbol) for symbol in symbols])))
        
    def print_exchange_info(self):
        print(f'{self.id}\n  count currencies: {len(self.currencies.keys())}\n  count markets: {len(self.markets.keys())}')

    def get_exchange(self)  -> ccxt.poloniex:
        try:
            if self.isApiWorking:
                exchange = getattr(ccxt, self.id)(self.infos)
            else:
                exchange = getattr(ccxt, self.id)
                
        except:
            print(f"Error creating exchange instance for {self.id}: {self.infos}")
            exchange = getattr(ccxt, self.id)
            self.isApiWorking = False
            print(f"Using default exchange instance for {self.id}")

        return exchange
    def get_exchange(self)  -> ccxt.poloniex:
        return getattr(ccxt, self.id)(self.infos)
    
    def get_networks_for_currency(self, symbol):
        currency = self.currencies.get(symbol)
        if currency: return currency.networks

    def get_symbols(self, market_keys):
        symbols={'currencies':['USDT'], 'markets':[]}

        for symbol in market_keys:
            a,b = symbol.split('/')
            if a=='USDT' or b=='USDT':
                currency=a if a != 'USDT' else b

                if currency not in symbols['currencies']:
                    symbols['currencies'].append(currency)

        for symbol in market_keys:
            a,b = symbol.split('/')
        
            if a in symbols['currencies'] and b in symbols['currencies']:
                symbols['markets'].append(symbol)

        return symbols
    
    async def fetch_fees(self):
        exchange=self.get_exchange()
        fees = await exchange.fetch_trading_fees()
        await exchange.close()
        return fees
    
    async def fetch_markets(self, exchange):
        return {market['symbol']:market for market in await exchange.fetch_markets()}
    
    async def fetch_currencies(self):
        exchange=self.get_exchange()
        currencies = await exchange.fetch_currencies()
        await exchange.close()
        return currencies
    

    def get_markets_for_currency(self, currency):
        out={}

        for mName, mInfo in self.markets.items():
            if mInfo['base'] == currency or mInfo['quote'] == currency:
                out[mName] = mInfo

        return out

    def get_market_by_symbol(self, symbol):
        return self.markets.get(symbol)
    
    def get_market_by_currencies(self, currency1, currency2):
        for mName, mInfo in self.markets.items():
            if (mInfo['base'] == currency1 and mInfo['quote'] == currency2) or (mInfo['base'] == currency2 and mInfo['quote'] == currency1):
                return mInfo
        
    def get_currency(self, symbol):
        return self.currencies.get(symbol)

    async def fetch_orderbook(self, symbol):
        try:
            exchange =self.get_exchange()
            orderbook = await exchange.fetch_order_book(symbol)
            exchange.close()

        except Exception as e:
            print(f"Error fetching order book for {symbol}: {e}")

        return orderbook
            



    def simulate_transfer(self, symbol, type, network, amount):
        amountOut = amount
        if type == 'withdraw':
            fee = self.currencies[symbol]['networks'][network].get('fee')
      
        if fee is not None:
            amountOut -= fee

        return {
            'currency': symbol,
            'amountIn': amount,
            'amountOut': amountOut,
            'type': type,
            'fee': fee,
            'network': network
        }
    