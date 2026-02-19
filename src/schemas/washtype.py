import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional

from src.models.washtype import WashType


class SWashTypeCreate(BaseModel):
    name: str = Field(...)
    description: Optional[str] = Field(None, min_length=1, max_length=100)
    duration_minutes: int = Field(...)
    base_price: float = Field(...)

    model_config = ConfigDict(from_attributes=True) 


    @field_validator("base_price", mode="before")
    @classmethod
    def validate_base_price(cls, values: float) -> float:
        if values < 0:
            raise ValueError("Базовая цена не может быть отрицательной")
        return values
    


class SWashTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, min_length=1, max_length=100)
    duration_minutes: Optional[int] = Field(None)
    base_price: Optional[float] = Field(None)

    model_config = ConfigDict(from_attributes=True)


class SWashTypeResponse(BaseModel):
    id: uuid.UUID = Field(...)
    name: str
    description: Optional[str]
    duration_minutes: int
    base_price: float

    model_config = ConfigDict(from_attributes=True)