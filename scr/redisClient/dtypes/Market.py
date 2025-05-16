from .base import *


class MarketTrade(TypedDict):
    currency_in     : str
    currency_out    : str
    amount_out      : float
    amount_in       : float
    price           : float

class Ticker(TypedDict):
    timestamp:  int     = Field(...,description="(64-bit Unix Timestamp in milliseconds since Epoch 1 Jan 1970)")
    bid:        float   = Field(...,description="current best bid (buy) price")
    ask:        float   = Field(...,description="current best ask (ask) price")
    close:      float   = Field(..., description="last price")

class Precision(TypedDict):
    amount: float       = Field(..., index=True)
    price:  float       = Field(..., index=True)

class Limits(TypedDict):
    amount: MinMax      = Field(..., index=True)
    price:  MinMax      = Field(..., index=True)
    cost:   MinMax      = Field(..., index=True)

class Fees(TypedDict):
    maker:      float   = Field(..., index=True)
    taker:      float   = Field(..., index=True)
    percentage: bool    = Field(..., index=True)

class OrderBook(TypedDict):
    ask: Optional[List] = Field([], index=True)
    bid: Optional[List] = Field([], index=True)

class Market(BaseModel):
    """
    needed:
        exchange, id, base, quote, spot, swap, active, precision, limits, fees, info
    """
    exchange:   str = Field(index=True)
    id:         str = Field(min_length=3, index=True)  # Symbol
    base:       str = Field(index=True)
    quote:      str = Field(index=True)
    spot:       bool = Field(index=True)
    swap:       bool = Field(index=True)
    active:     bool = Field(index=True)
    precision:  Precision = Field(index=True)
    limits:     Limits = Field(index=True)
    fees:       Fees = Field(index=True)
    info:       Dict[str, Any] = Field(index=True)
    ticker:     Optional[Ticker] = Field(None)
    orderbook:  Optional[OrderBook] = Field(None)


    def update_fields(self, **field_values):
        if field_values['exchange'] != self.exchange or field_values['id'] != self.id:
            raise Exception('field values not matching class')
        self.update({k:v for k,v in field_values.items()})


    @classmethod
    def init_update(cls, **field_values):
        return cls._init_update(((Market.id == field_values['id']) & (Market.exchange == field_values['exchange'])), **field_values)
    
    @classmethod
    def init(cls, exchange: str, id: str, base: str, quote: str, spot: bool, swap: bool,
                active: bool, precision: Precision, limits: Limits, fees: Fees, info: Dict[str, Any],
                ticker: Optional[Ticker] = None, orderbook: Optional[OrderBook] = None):
        return cls(**cls.as_dict(exchange,id,base,quote,spot,swap,active,precision,limits,fees,info,ticker,orderbook))
   
    @classmethod
    def as_dict(cls, exchange: str, id: str, base: str, quote: str, spot: bool, swap: bool,
                active: bool, precision: Precision, limits: Limits, fees: Fees, info: Dict[str, Any],
                ticker: Optional[Ticker] = None, orderbook: Optional[OrderBook] = None):
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
            'info': info,
            'ticker': ticker,
            'orderbook': orderbook
        }
        
    @classmethod
    def as_expression(cls, **field_values):
        ex = {}
        for k, v in field_values.items():
            match k:
                case 'exchange':
                    ex[k] = Market.exchange == v
                case 'id':
                    ex[k] = Market.id == v
                case 'base':
                    ex[k] = Market.base == v
                case 'quote':
                    ex[k] = Market.quote == v
                case 'spot':
                    ex[k] = Market.spot == v
                case 'swap':
                    ex[k] = Market.swap == v
                case 'active':
                    ex[k] = Market.active == v
                case 'precision':
                    if v != None:
                        for sk,sv in v.items():
                            match sk:
                                case 'amount':
                                    ex[f'{k}_{sk}'] = Market.precision.amount == sv
                                case 'price':
                                    ex[f'{k}_{sk}'] = Market.precision.price == sv
                                case _:
                                    continue
                case 'limits':
                    if v != None:
                        for sk, sv in v.items():
                            match sk:
                                case 'amount':
                                    d = Market.limits.amount
                                case 'price':
                                    d = Market.limits.price
                                case 'cost':
                                    d = Market.limits.cost
                                case _:
                                    continue
                            ex[f'{k}_{sk}_max'] = d.max == sv.get('max')
                            ex[f'{k}_{sk}_min'] = d.min == sv.get('min')

                case 'fees':
                    if v != None:
                        d = Market.fees
                        for sk, sv in v.items():
                            match sk:
                                case 'maker':
                                    ex[f'{k}_{sk}'] = d.maker == sv
                                case 'taker':
                                    ex[f'{k}_{sk}'] = d.taker == sv
                                case 'percentage':
                                    ex[f'{k}_{sk}'] = d.percentage == sv

                    ex[k] = Market.fees == v
                case 'ticker':
                    ex[k] = Market.ticker == v
                case 'orderbook':
                    ex[k] = Market.orderbook == v
                case _:
                    continue

        return ex

    @classmethod
    def _format_precision(cls, amount, price):
        return {'amount':amount, 'price':price}
    
    @classmethod
    def _format_limits(cls, amount:tuple, price:tuple, cost:tuple):
        return {'amount': {'min': amount[0], 'max': amount[1]}, 'price': {'min': price[0], 'max': price[1]}, 'cost': {'min': cost[0], 'max': cost[1]}} 
 

    @field_validator('id')
    @classmethod
    def _validate_id_format(cls, v: str) -> str:
        v = v.replace('-', '/').replace('_', '/')
        if '/' not in v or len(v.split('/')) != 2:
            raise ValueError("symbol must be 'BASE/QUOTE'")
        return v

    @field_validator('precision', mode='before')
    @classmethod
    def _coerce_precision(cls, v: Any) -> Precision:
        # Expect v either dict or correct type
        return Precision(**(v if isinstance(v, dict) else v.__dict__))

    async def update_ticker(self, timestamp, bid, ask, close):
        self.update(**dict(timestamp=timestamp, bid=bid, ask=ask, close=close))

    async def update_orderbook(self, bid, ask):
        await self.update(**dict(bid=bid, ask=ask))

    def simulate_order(self, currency_in, amount_in):
        trades = []
        remaining = amount_in
        amount_out = 0.0

        if currency_in == self.quote:
            side = 'buy'
            currency_out=self.quote
        else:
            side = 'sell'
            currency_out=self.base

        ob = self.get_orderbook(side)
        
        for price, volume in ob:
            if side == 'buy':
                remaining   = remaining / price
            
            take        = min(remaining, volume)
            remaining   -= take

            amount = self.calc_return(take, price, side, 'taker')
            amount_out  += amount

            trades.append(price, take, remaining, amount)
           
            if side == 'buy':
                remaining*=price

            if remaining <=0:
                break

        if remaining > 0:
            raise RuntimeError(f"{self.id} - Nicht genug Liquidität im Orderbuch für {amount_in} {currency_in}")
        
        price = (amount_in / amount_out) if side == 'buy' else (amount_out / amount_in)

        return MarketTrade(**{
            'currency_in'   : currency_in,
            'currency_out'  : currency_out,
            'amount_in'     : amount_in,
            'amount_out'    : amount_out,
            'price'         : price,
            'trades'        : trades
        })
            
    def get_orderbook(self, side:Literal['buy', 'sell']):
        if side == 'buy':
            return self.orderbook.ask
        else:
            return self.orderbook.bid
        
    def get_last_orderbook_price(self, side:Literal['buy', 'sell']):
        if side == 'buy':
            return self.ticker.ask
        else:
            return self.ticker.bid
        
    def calc_return(self, volume:float, price:float, side:Literal['buy', 'sell'], feeType:Literal['maker', 'taker']='taker'):
        if side == 'buy':
            fee = 1 + self.fees.taker if feeType == 'taker' else self.fees.maker

            if self.fees.percentage:
                amount = volume / (price*fee)
            else:
                amount = (volume / price) - fee

        else:
            fee = 1 - self.fees.taker if feeType == 'taker' else self.fees.maker

            if self.fees.percentage:
                amount = volume * (price*fee)
            else:
                amount = (volume * price) - fee

        return amount

