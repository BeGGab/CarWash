import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class SWashBayCreate(BaseModel):
    """Схема создания бокса мойки"""
    car_wash_id: uuid.UUID
    bay_number: int = Field(..., ge=1)
    bay_type: str = Field(..., min_length=1, max_length=50)
    is_active: bool = True
    
    model_config = ConfigDict(from_attributes=True)


class SWashBayUpdate(BaseModel):
    """Схема обновления бокса мойки"""
    bay_number: Optional[int] = Field(None, ge=1)
    bay_type: Optional[str] = Field(None, min_length=1, max_length=50)
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)


class SWashBayResponse(BaseModel):
    """Схема ответа бокса мойки"""
    id: uuid.UUID
    car_wash_id: uuid.UUID
    bay_number: int
    bay_type: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class SWashBayListResponse(BaseModel):
    """Список боксов мойки"""
    items: List[SWashBayResponse]
    total: int
