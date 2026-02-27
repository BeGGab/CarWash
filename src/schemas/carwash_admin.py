import uuid
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class SCarWashAdminBase(BaseModel):
    user_id: int
    car_wash_id: uuid.UUID


class SCarWashAdminCreate(SCarWashAdminBase):
    pass


class SCarWashAdmin(SCarWashAdminBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class SCarWashAdminResponse(SCarWashAdmin):
    """Схема ответа с информацией о пользователе."""

    user_name: Optional[str] = None
    user_phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SCarWashAdminListResponse(BaseModel):
    """Схема для списка администраторов."""

    items: List[SCarWashAdminResponse]
