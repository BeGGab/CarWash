"""
Схемы данных для работы с платежами
"""
import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SPaymentCreate(BaseModel):
    """Запрос на создание платежа"""

    booking_id: uuid.UUID
    return_url: str  # URL для возврата после оплаты

    model_config = ConfigDict(from_attributes=True)


class SPaymentResponse(BaseModel):
    """Ответ с данными платежа"""

    payment_id: str
    booking_id: uuid.UUID
    amount: float
    currency: str = "RUB"
    status: str
    confirmation_url: Optional[str] = None  # URL для оплаты
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SPaymentCallback(BaseModel):
    """Callback от платежной системы"""

    event: str  # payment.succeeded, payment.canceled, etc.
    payment_id: str
    booking_id: uuid.UUID
    status: str
    amount: float

    model_config = ConfigDict(from_attributes=True)


class SRefundRequest(BaseModel):
    """Запрос на возврат"""

    booking_id: uuid.UUID
    amount: Optional[float] = None  # None = полный возврат
    reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SRefundResponse(BaseModel):
    """Ответ на запрос возврата"""

    refund_id: str
    booking_id: uuid.UUID
    amount: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
