from aredis_om import JsonModel, EmbeddedJsonModel, get_redis_connection, Field, NotFoundError
from typing import Dict, Any, List, Optional, Union, Literal, TypedDict, ClassVar
from pydantic import field_validator
from logger import log
from .. import connectionPool

def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """
    Recursively flattens a nested dict.

    :param d: The input dictionary (possibly nested).
    :param parent_key: The prefix for current recursion (used internally).
    :param sep: Separator between key levels.
    :return: A new flat dict where nested keys are joined by sep.
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            # Recurse into sub-dictionary
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


class BaseModel(JsonModel):
    """Base class adding update check"""
    class Meta:
        database    = get_redis_connection(connectionPool)

    @classmethod
    def log(cls, title, level, msg):
        log(cls.__class__.__name__, title, level, msg)

    @classmethod
    def as_dict(cls, **field_values):
        return {}

    @classmethod
    def as_expression(cls, **field_values):
        return {}

    @classmethod
    def find_item(cls, **field_values):
        return cls()
    
    def update_fields(self, **field_values):
        pass

    @classmethod 
    async def init(cls, **field_values):
        instance = cls(**field_values)
        await instance.save()
        return instance
    
    # Model initiation
    @classmethod 
    async def _init_update(cls, expression, **field_values):
        try:
            ob = await cls.find(expression).first()
            ob.update_fields(**field_values)

        except NotFoundError as e:
            ob = cls.init(**field_values)
            await ob.save()

        except Exception as e:
            cls.log('UPDATE', 'error', f'update failed - {field_values['contractAddress']} - {e}')
            return
        cls.log('UPDATE', 'info', f'update success - {field_values['contractAddress']}')

class MinMax(TypedDict):
    min: Optional[float] = Field(..., index=True)
    max: Optional[float] = Field(..., index=True)

