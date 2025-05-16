from .base import *

class Currency(BaseModel):
    exchange:   str             = Field(..., min_length=1, index=True)
    id:         str             = Field(..., min_length=1, index=True)
    symbol:     str             = Field(..., min_length=1, index=True)
    deposit:    bool            = Field(..., index=True)
    withdraw:   bool            = Field(..., index=True)
    active:     bool            = Field(..., index=True)
    info:       Dict[str, Any]  = Field(..., index=True)
    networks:   List[str]       = Field([], index=True)
    

    def update_fields(self, **field_values):
        if field_values['exchange'] != self.exchange or field_values['id'] != self.id:
            raise Exception('field values not matching class')
        
        self.update({k:v for k,v in field_values.items()})

    @classmethod
    def init_update(cls, **field_values):
        return cls._init_update(((Currency.id == field_values['id']) & (Currency.exchange == field_values['exchange'])), **field_values)

    @classmethod
    def init(cls, exchange: str, id: str, symbol: str, deposit: bool = False,
                withdraw: bool = False, active: bool = False, info: dict = {}, networks: list = []):
        return cls(**{
            'exchange'  : exchange,
            'id'        : id,
            'symbol'    : symbol,
            'deposit'   : deposit,
            'withdraw'  : withdraw,
            'active'    : active,
            'info'      : info,
            'networks'  : networks
        })
    

    @classmethod
    def as_expression(cls, **field_values):
        ex = {}
        for k, v in field_values.items():
            match k:
                case 'exchange':
                    ex[k] = Currency.exchange == v
                case 'id':
                    ex[k] = Currency.id == v
                case 'symbol':
                    ex[k] = Currency.symbol == v
                case 'deposit':
                    ex[k] = Currency.deposit == v
                case 'withdraw':
                    ex[k] = Currency.withdraw == v
                case 'active':
                    ex[k] = Currency.active == v
                case 'networks':
                    if v != None:
                        for i in range(len(v)):
                            ex[f'{k}_{i}'] = v[i] in Currency.networks
                case _:
                    continue
     
        return ex  


    @field_validator('id')
    @classmethod
    def _validate_id(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('id cannot be empty')
        return v

    @field_validator('symbol', mode='before')
    @classmethod
    def _validate_symbol(cls, v: str) -> str:
        if not v.isupper():
            v=v.upper()
        return v

    @field_validator('deposit', 'withdraw', 'active')
    @classmethod 
    def _validate_flags(cls, v: bool) -> bool:
        if not isinstance(v, bool):
            raise ValueError('flag must be a boolean')
        return v
    
    @field_validator('networks', 'withdraw', 'active')
    @classmethod 
    def _validate_networks(cls, v: list) -> list:
        if not isinstance(v, list):
            raise ValueError('flag must be a list')
        return v
