import re
import uuid
from datetime import datetime
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    EmailStr,
    field_validator,
    model_validator,
)

from typing import Optional

from src.models.users import User


class SPhoneVerification(BaseModel):
    telegram_id: int = Field(...)
    phone_number: str = Field(...)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone_number(cls, values: str) -> str:
        if not values:
            return values
        if not re.match(r"^\+7\d{10}$", values):
            values = "+7" + values[1:]
        return values


class SUserCreate(BaseModel):
    telegram_id: int = Field(...)
    username: str = Field(..., min_length=3, max_length=32)
    email: Optional[EmailStr] = Field(None)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone_number: Optional[str] = Field(None)
    is_verified: bool = Field(False)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, values: str) -> str:
        if not values or not re.match(r"^[a-zA-Z0-9_]+$", values):
            raise ValueError(
                "Username не должен быть пустым и может содержать только буквы, цифры и '_'"
            )
        return values

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone_number(cls, values: str) -> str:
        if not values:
            return values
        if not re.match(r"^\+7\d{10}$", values):
            values = "+7" + values[1:]
        return values

    def to_orm_model(self) -> User:
        user = User(**self.model_dump())
        return user


class SUserUpdate(BaseModel):
    telegram_id: Optional[int] = Field(None)
    username: Optional[str] = Field(None, min_length=5, max_length=16)
    email: Optional[EmailStr] = Field(None)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone_number: Optional[SPhoneVerification] = Field(None)
    is_verified: Optional[bool] = Field(None)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, values: str) -> str:
        if values and not re.match(r"^[a-zA-Z0-9_]+$", values):
            raise ValueError("Username может содержать только буквы, цифры и '_'")
        return values

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, values: str) -> str:
        if not values or values == "":
            return ValueError(f"Email - не должен быть пустой строкой")
        return values

    @model_validator(mode="after")
    def validate_update_data(self) -> "SUserUpdate":
        update_fields = self.model_dump(exclude_unset=True, exclude_none=True)
        update_fields.pop("telegram_id", None)
        if not update_fields:
            raise ValueError("Нет данных для обновления")
        return self

    def apply_update(self, user: User) -> None:
        for field, value in self.model_dump().items():
            if value is not None:
                setattr(user, field, value)


class SUserResponse(BaseModel):
    id: uuid.UUID = Field(...)
    telegram_id: Optional[int] = Field(None)
    username: str
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str] = None
    is_verified: bool
    total_bookings: int = 0
    completed_bookings: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class STelegramAuth(BaseModel):
    """Авторизация через Telegram"""

    telegram_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str

    model_config = ConfigDict(from_attributes=True)
