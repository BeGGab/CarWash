import uuid
from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


class SBookingCreate(BaseModel):
    """Схема создания бронирования"""

    telegram_id: int
    user_id: Optional[uuid.UUID]
    car_wash_id: uuid.UUID
    wash_bay_id: uuid.UUID
    time_slot_id: uuid.UUID
    wash_type_id: uuid.UUID

    guest_phone: str = Field(..., min_length=10)
    guest_name: str = Field(..., min_length=1, max_length=100)

    car_plate: str = Field(..., min_length=1, max_length=20)
    car_model: str = Field(..., min_length=1, max_length=50)

    slot_date: date
    start_time: time
    end_time: time

    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("guest_phone", mode="before")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        phone = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if phone.startswith("8"):
            phone = "+7" + phone[1:]
        if not phone.startswith("+7"):
            phone = "+7" + phone
        return phone


class SBookingUpdate(BaseModel):
    """Схема обновления бронирования"""

    status: Optional[str] = None
    payment_status: Optional[str] = None
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SBookingResponse(BaseModel):
    """Схема ответа бронирования"""

    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    car_wash_id: uuid.UUID
    wash_bay_id: uuid.UUID
    time_slot_id: uuid.UUID
    wash_type_id: uuid.UUID

    guest_phone: str
    guest_name: str
    car_plate: str
    car_model: str

    booking_date: datetime
    slot_date: date
    start_time: time
    end_time: time
    duration_minutes: int

    price: float
    discount: float
    final_price: float

    status: str
    payment_status: str

    notes: Optional[str]
    cancellation_reason: Optional[str]

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SBookingWithDetails(SBookingResponse):
    """Бронирование с деталями"""

    car_wash_name: Optional[str] = None
    car_wash_address: Optional[str] = None
    wash_type_name: Optional[str] = None
    bay_number: Optional[int] = None
    qr_code: Optional[str] = None


class SBookingListResponse(BaseModel):
    """Список бронирований с пагинацией"""

    items: List[SBookingWithDetails]
    total: int
    page: int
    per_page: int
    pages: int


class SPaymentInfo(BaseModel):
    """Информация для оплаты"""

    booking_id: uuid.UUID
    amount: float
    prepayment_amount: float  # 50% предоплата
    currency: str = "RUB"
    payment_url: Optional[str] = None
    expires_at: datetime


class SBookingConfirmation(BaseModel):
    """Подтверждение бронирования"""

    booking: SBookingWithDetails
    payment: SPaymentInfo
    qr_code: str

    model_config = ConfigDict(from_attributes=True)


class STelegramInitData(BaseModel):
    """Данные инициализации Telegram Mini App"""

    telegram_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
