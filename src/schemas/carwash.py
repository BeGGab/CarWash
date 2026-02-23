import re
import uuid
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator

from typing import Optional

from src.models.carwash import CarWash


class SCarWashCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    address: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(...)
    working_hours: dict = Field(...)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, values: str) -> str:
        if not values or not values.strip():
            raise ValueError("Название мойки не может быть пустым")
        return values

    @field_validator("address", mode="before")
    @classmethod
    def validate_address(cls, values: str) -> str:
        if not values or not values.strip():
            raise ValueError("Адрес мойки не может быть пустым")
        return values

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone_number(cls, values: str) -> str:
        if not re.match(r"^\+7\d{10}$", values):
            raise ValueError(
                'Номер телефона должен начинаться с "+7" и содержать 10 цифр.'
            )
        return values

    @field_validator("working_hours", mode="before")
    @classmethod
    def validate_working_hours(cls, values: dict) -> dict:
        if not isinstance(values, dict):
            raise ValueError("Рабочие часы должны быть словарем")
        if "start" not in values or "end" not in values:
            raise ValueError("Рабочие часы должны содержать 'start' и 'end'")
        try:
            start_hour = int(values["start"].split(":")[0])
            end_hour = int(values["end"].split(":")[0])
            if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23):
                raise ValueError("Часы работы должны быть в диапазоне от 00 до 23")
            if start_hour >= end_hour:
                raise ValueError(
                    "Время начала работы должно быть раньше времени окончания"
                )
        except (ValueError, TypeError):
            raise ValueError(
                "Неверный формат времени в рабочих часах. Используйте 'HH:MM'"
            )
        return values

    def to_orm_model(self) -> CarWash:
        carwash = CarWash(**self.model_dump())
        return carwash


class SCarWashUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    address: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None)
    working_hours: Optional[dict] = Field(None)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, values: str) -> str:
        if not values or not values.strip():
            raise ValueError("Название мойки не может быть пустым")
        return values

    @field_validator("address", mode="before")
    @classmethod
    def validate_address(cls, values: str) -> str:
        if not values or not values.strip():
            raise ValueError("Адрес мойки не может быть пустым")
        return values

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone_number(cls, values: str) -> str:
        if not re.match(r"^\+7\d{10}$", values):
            raise ValueError(
                'Номер телефона должен начинаться с "+7" и содержать 10 цифр.'
            )
        return values

    @field_validator("working_hours", mode="before")
    @classmethod
    def validate_working_hours(cls, values: dict) -> dict:
        if not isinstance(values, dict):
            raise ValueError("Рабочие часы должны быть словарем")
        if "start" not in values or "end" not in values:
            raise ValueError("Рабочие часы должны содержать 'start' и 'end'")
        try:
            start_hour = int(values["start"].split(":")[0])
            end_hour = int(values["end"].split(":")[0])
            if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23):
                raise ValueError("Часы работы должны быть в диапазоне от 00 до 23")
            if start_hour >= end_hour:
                raise ValueError(
                    "Время начала работы должно быть раньше времени окончания"
                )
        except (ValueError, TypeError):
            raise ValueError(
                "Неверный формат времени в рабочих часах. Используйте 'HH:MM'"
            )
        return values

    @model_validator(mode="after")
    def validate_update_data(self) -> "SCarWashUpdate":
        update_fields = self.model_dump(exclude_unset=True, exclude_none=True)
        if not update_fields:
            raise ValueError("Нет данных для обновления")
        return self

    def apply_update(self, carwash: CarWash) -> None:
        for field, value in self.model_dump().items():
            if value is not None:
                setattr(carwash, field, value)


class SCarWashResponse(BaseModel):
    id: uuid.UUID = Field(...)
    name: str
    address: str
    phone_number: str
    working_hours: dict

    model_config = ConfigDict(from_attributes=True)
