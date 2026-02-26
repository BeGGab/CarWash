import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class SWashTypeCreate(BaseModel):
    """Схема создания типа мойки"""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    duration_minutes: int = Field(..., ge=10, le=480)
    base_price: float = Field(..., ge=0)

    model_config = ConfigDict(from_attributes=True)


class SWashTypeUpdate(BaseModel):
    """Схема обновления типа мойки"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    duration_minutes: Optional[int] = Field(None, ge=10, le=480)
    base_price: Optional[float] = Field(None, ge=0)

    model_config = ConfigDict(from_attributes=True)


class SWashTypeResponse(BaseModel):
    """Схема ответа типа мойки"""

    id: uuid.UUID
    name: str
    description: str
    duration_minutes: int
    base_price: float

    model_config = ConfigDict(from_attributes=True)


class SWashTypeListResponse(BaseModel):
    """Список типов мойки"""

    items: List[SWashTypeResponse]
    total: int
