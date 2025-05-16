from .base import *

class FeeData(EmbeddedJsonModel):
    fee:        Optional[float] = Field(..., index=True)
    percentage: Optional[bool]  = Field(..., index=True)

class Fees(EmbeddedJsonModel):
    withdraw: Optional[FeeData] = Field(..., index=True)
    deposit:  Optional[FeeData] = Field(..., index=True)

    @field_validator('withdraw', 'deposit', mode='before')
    @classmethod
    def _coerce_withdraw_deposit(cls, v: Any) -> float:
        if type(v) == int:
            v = float(v)
        return v
    
    @field_validator('withdraw')
    @classmethod
    def _coerce_withdraw(cls, v: Any):
        if v == None:
            raise ValueError("Fee cannot be None")
        
class Limits(EmbeddedJsonModel):
    withdraw: MinMax = Field(..., index=True)
    deposit:  MinMax = Field(..., index=True)


class Network(BaseModel):
    exchange: str = Field(..., min_length=1, index=True)
    currency: str = Field(..., min_length=1, index=True)
    withdraw: bool = Field(..., index=True)
    deposit: bool = Field(..., index=True)
    active: bool = Field(..., index=True)
    precision: Optional[float] = Field(..., ge=0, index=True)
    fees: Fees = Field(..., index=True)
    limits: Limits = Field(..., index=True)
    names: List[str] = Field(..., index=True)
    depositAddress:     Optional[str] = Field(None, min_length=1, index=True)
    contractAddress:    Optional[str] = Field(None, min_length=1, index=True)
    info: Dict[str, Any] = Field(..., index=True)
    id: Optional[str] = Field(None, index=True)


    @classmethod
    def init_update(cls, **field_values):
        return cls._init_update(((Network.contractAddress == field_values['contractAddress']) & (Network.exchange == field_values['exchange'])), **field_values)
    
    @classmethod
    def init(cls, exchange: str, currency: str, withdraw: bool, deposit: bool, active: bool,
                precision: Optional[float], fees: Fees, limits: Limits, names: List[str],
                depositAddress: Optional[str] = None, contractAddress: Optional[str] = None,
                info: Dict[str, Any] = {}, id: Optional[str] = None):
        return cls(**{
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
        })
    
    
    @classmethod
    def as_expression(cls, **field_values):
        ex = {}
        for k, v in field_values.items():
            match k:
                case 'exchange':
                    ex[k] = Network.exchange == v
                case 'currency':
                    ex[k] = Network.currency == v
                case 'withdraw':
                    ex[k] = Network.withdraw == v
                case 'deposit':
                    ex[k] = Network.deposit == v
                case 'active':
                    ex[k] = Network.active == v
                case 'precision':
                    ex[k] = Network.precision == v
                case 'fees':
                    if v != None:
                        for sk, sv in v.items():
                            match sk:
                                case 'withdraw':
                                    d = Network.fees.withdraw
                                case 'deposit':
                                    d = Network.fees.deposit
                                case _:
                                    continue
                            ex[f'{k}_{sk}_fee'] = d.fee == sv.get('fee')
                            ex[f'{k}_{sk}_percentage'] = d.percentage == sv.get('percentage')

                case 'limits':
                    if v != None:
                        d = Network.limits
                        for sk, sv in v.items():
                            match sk:
                                case 'withdraw':
                                    d=d.withdraw
                                case 'deposit':
                                    d=d.deposit
                                case _:
                                    continue
                            ex[f'{k}_{sk}_max'] = d.max == sv.get('max')
                            ex[f'{k}_{sk}_min'] = d.min == sv.get('min')
                case 'names':
                    ex[k] = Network.names == v
                case 'depositAddress':
                    ex[k] = Network.depositAddress == v
                case 'contractAddress':
                    ex[k] = Network.contractAddress == v
                case 'id':
                    ex[k] = Network.id == v
                case _:
                    continue
            

        return ex
    
    @field_validator('precision', mode='before')
    @classmethod
    def _coerce_precision(cls, v: Any) -> float:
        if isinstance(v, str):
            return float(v)
        if isinstance(v, int):
            return 1 / (10 ** v)
        return v

    @field_validator('contractAddress')
    @classmethod
    def _validate_contract_address(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < 2:
            raise ValueError('invalid contractAddress')
        return v

    def calculate_deposit(self, amount):
        self.check_limits(amount, 'deposit')

        if self.fees.deposit.percentage==True:
            return amount * (1-self.fees.deposit.fee)

        elif self.fees.deposit.percentage==False:
            return amount - self.fees.deposit.fee
        
        else:
            return amount

    def calculate_withdraw(self, amount):
        self.check_limits(amount, 'withdraw')

        if self.fees.withdraw.percentage==True:
            return amount * (1-self.fees.withdraw.fee)

        elif self.fees.withdraw.percentage==False:
            return amount - self.fees.withdraw.fee
        
        else:
            return amount
    
    def check_limits(self, amount, type):
        if type == 'withdraw':
            if amount <= self.limits.withdraw.min:
                raise Exception(f'amount below limit: {amount} / {self.limits.withdraw.min}')
            elif amount >= self.limits.withdraw.max:
                raise Exception(f'amount above limit: {amount} / {self.limits.withdraw.max}')
        else:
            if amount <= self.limits.deposit.min:
                raise Exception(f'amount below limit: {amount} / {self.limits.deposit.min}')
            elif amount >= self.limits.deposit.max:
                raise Exception(f'amount above limit: {amount} / {self.limits.deposit.max}')   
