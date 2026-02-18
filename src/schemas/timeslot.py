import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


from src.models.timeslot import TimeSlot




class STimeCreate(BaseModel):
    carwash_id: uuid.UUID = Field(...)
    date: datetime = Field(...)
    time: str = Field(...)
    is_booked: bool = Field(default=False)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("time", mode="before")
    @classmethod
    def validate_time(cls, values: str) -> str:
        if not values or not values.strip():
            raise ValueError("Время не может быть пустым")
        if not re.match(r"^\d{2}:\d{2}$", values):
            raise ValueError("Неверный формат времени. Используйте 'HH:MM'")
        return values


class STimeUpdate(BaseModel):
    carwash_id: Optional[uuid.UUID] = Field(None)
    date: Optional[datetime] = Field(None)
    time: Optional[str] = Field(None)
    is_booked: Optional[bool] = Field(None)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("time", mode="before")
    @classmethod
    def validate_time(cls, values: str) -> str:
        if not values or not values.strip():
            raise ValueError("Время не может быть пустым")
        if not re.match(r"^\d{2}:\d{2}$", values):
            raise ValueError("Неверный формат времени. Используйте 'HH:MM'")
        return values

    @model_validator(mode="after")
    def validate_update_data(self) -> "STimeUpdate":
        update_fields = self.model_dump(exclude_unset=True, exclude_none=True)
        if not update_fields:
            raise ValueError("Нет данных для обновления")
        return self


class STimeResponse(BaseModel):
    id: uuid.UUID = Field(...)
    carwash_id: uuid.UUID
    date: datetime
    time: str
    is_booked: bool

    model_config = ConfigDict(from_attributes=True)