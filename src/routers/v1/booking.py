"""
API роутер для работы с бронированиями
"""
import uuid
from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session

from src.schemas.booking import (
    SBookingCreate, 
    SBookingWithDetails,
    SBookingListResponse,
    SBookingConfirmation
)

from src.services.booking import (
    create_booking_service,
    get_my_bookings_service,
    get_booking_by_id_service,
    cancel_booking_service,
    get_carwash_bookings_service,
    start_wash_service,
    complete_wash_service,
    verify_qr_service,
)

router = APIRouter(prefix="/api/v1/bookings", tags=["Bookings"])





# ==================== Эндпоинты для клиентов ====================

@router.post("/create")
async def create(
    data: SBookingCreate,
    session: AsyncSession = Depends(get_async_session),
) -> SBookingConfirmation:
    return await create_booking_service(data, session)





@router.get("/my", response_model=SBookingListResponse)
async def get_my_bookings(
    phone: str = Query(..., description="Телефон пользователя"),
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Получить мои бронирования по номеру телефона
    
    Статусы:
    - pending_payment - ожидает оплаты
    - confirmed - подтверждено
    - in_progress - выполняется
    - completed - завершено
    - cancelled - отменено
    """
    return await get_my_bookings_service(
        phone=phone,
        status=status,
        page=page,
        per_page=per_page,
        session=session,
    )


@router.get("/{booking_id}", response_model=SBookingWithDetails)
async def get_booking(
    booking_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """Получить бронирование по ID"""
    return await get_booking_by_id_service(booking_id, session)


@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: uuid.UUID,
    reason: Optional[str] = Query(None, description="Причина отмены"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Отменить бронирование
    
    - Можно отменить за 2+ часа до начала
    - Возврат средств согласно политике
    """
    return await cancel_booking_service(booking_id, reason, session)


# ==================== Эндпоинты для админов автомоек ====================

@router.get("/admin/carwash/{carwash_id}", response_model=SBookingListResponse)
async def get_carwash_bookings(
    carwash_id: uuid.UUID,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session),
):
    """Получить бронирования автомойки (для админов мойки)"""
    return await get_carwash_bookings_service(
        carwash_id=carwash_id,
        date_from=date_from,
        date_to=date_to,
        status=status,
        page=page,
        per_page=per_page,
        session=session,
    )


@router.post("/admin/{booking_id}/start")
async def start_wash(
    booking_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """Начать мойку (сканирование QR)"""
    return await start_wash_service(booking_id, session)


@router.post("/admin/{booking_id}/complete")
async def complete_wash(
    booking_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """Завершить мойку"""
    return await complete_wash_service(booking_id, session)


@router.post("/admin/{booking_id}/verify-qr")
async def verify_qr(
    booking_id: uuid.UUID,
    qr_code: str = Query(..., description="QR-код клиента"),
    session: AsyncSession = Depends(get_async_session),
):
    """Проверить QR-код клиента"""
    return await verify_qr_service(booking_id, qr_code, session)
