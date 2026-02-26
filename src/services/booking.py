import uuid
from typing import Optional
from datetime import datetime, date, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from src.repositories.booking import BookingRepository

from src.schemas.booking import (
    SBookingCreate,
    SPaymentInfo,
    SBookingConfirmation,
    SBookingUpdate,
    SBookingResponse,
    SBookingWithDetails,
    SBookingListResponse,
)


async def create_booking_service(
    data: SBookingCreate, session: AsyncSession
) -> SBookingConfirmation:
    """
    Сервисная функция для создания бронирования.
    1. Вызывает репозиторий для создания записи в БД.
    2. Формирует полный ответ SBookingConfirmation.
    """
    repo = BookingRepository(session)

    # 1. Создаем бронирование через репозиторий
    booking, slot, carwash, wash_type = await repo.create_booking(data)

    # 2. Генерируем QR-код
    qr_data = repo.generate_qr_data(booking.id, booking.guest_phone)

    # 3. Формируем детальную схему бронирования
    booking_details = SBookingWithDetails(
        id=booking.id,
        user_id=booking.user_id,
        car_wash_id=booking.car_wash_id,
        wash_bay_id=booking.wash_bay_id,
        time_slot_id=booking.time_slot_id,
        wash_type_id=booking.wash_type_id,
        guest_phone=booking.guest_phone,
        guest_name=booking.guest_name,
        car_plate=booking.car_plate,
        car_model=booking.car_model,
        booking_date=booking.booking_date,
        slot_date=booking.slot_date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        duration_minutes=booking.duration_minutes,
        price=booking.price,
        discount=booking.discount,
        final_price=booking.final_price,
        status=booking.status,
        payment_status=booking.payment_status,
        notes=booking.notes,
        cancellation_reason=booking.cancellation_reason,
        created_at=booking.created_at,
        car_wash_name=carwash.name,
        car_wash_address=carwash.address,
        wash_type_name=wash_type.name,
        bay_number=slot.wash_bay.bay_number if slot.wash_bay else None,
        qr_code=qr_data,
    )

    # 4. Формируем информацию для оплаты
    prepayment_amount = booking.final_price * 0.5
    payment_info = SPaymentInfo(
        booking_id=booking.id,
        amount=booking.final_price,
        prepayment_amount=prepayment_amount,
        currency="RUB",
        payment_url=f"/api/v1/payments/create",  # URL для создания платежа
        expires_at=booking.expires_at,
    )

    # 5. Возвращаем итоговый объект
    return SBookingConfirmation(
        booking=booking_details, payment=payment_info, qr_code=qr_data
    )


async def get_my_bookings_service(
    phone: str,
    status: Optional[str],
    page: int,
    per_page: int,
    session: AsyncSession,
) -> SBookingListResponse:
    """Сервисная функция для получения бронирований пользователя."""
    repo = BookingRepository(session)
    bookings, total = await repo.get_by_phone(
        phone=phone, status=status, page=page, per_page=per_page
    )

    items = []
    for b in bookings:
        qr_data = (
            repo.generate_qr_data(b.id, b.guest_phone)
            if b.status == "confirmed"
            else None
        )

        items.append(
            SBookingWithDetails(
                id=b.id,
                user_id=b.user_id,
                car_wash_id=b.car_wash_id,
                wash_bay_id=b.wash_bay_id,
                time_slot_id=b.time_slot_id,
                wash_type_id=b.wash_type_id,
                guest_phone=b.guest_phone,
                guest_name=b.guest_name,
                car_plate=b.car_plate,
                car_model=b.car_model,
                booking_date=b.booking_date,
                slot_date=b.slot_date,
                start_time=b.start_time,
                end_time=b.end_time,
                duration_minutes=b.duration_minutes,
                price=b.price,
                discount=b.discount,
                final_price=b.final_price,
                status=b.status,
                payment_status=b.payment_status,
                notes=b.notes,
                cancellation_reason=b.cancellation_reason,
                created_at=b.created_at,
                car_wash_name=b.car_wash.name if b.car_wash else None,
                car_wash_address=b.car_wash.address if b.car_wash else None,
                wash_type_name=b.wash_type.name if b.wash_type else None,
                bay_number=b.wash_bay.bay_number if b.wash_bay else None,
                qr_code=qr_data,
            )
        )

    pages = (total + per_page - 1) // per_page

    return SBookingListResponse(
        items=items, total=total, page=page, per_page=per_page, pages=pages
    )


async def get_booking_by_id_service(
    booking_id: uuid.UUID, session: AsyncSession
) -> SBookingWithDetails:
    """Сервисная функция для получения одного бронирования по ID."""
    repo = BookingRepository(session)
    booking = await repo.get_by_id(booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    qr_data = (
        repo.generate_qr_data(booking.id, booking.guest_phone)
        if booking.status == "confirmed"
        else None
    )

    return SBookingWithDetails(
        id=booking.id,
        user_id=booking.user_id,
        car_wash_id=booking.car_wash_id,
        wash_bay_id=booking.wash_bay_id,
        time_slot_id=booking.time_slot_id,
        wash_type_id=booking.wash_type_id,
        guest_phone=booking.guest_phone,
        guest_name=booking.guest_name,
        car_plate=booking.car_plate,
        car_model=booking.car_model,
        booking_date=booking.booking_date,
        slot_date=booking.slot_date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        duration_minutes=booking.duration_minutes,
        price=booking.price,
        discount=booking.discount,
        final_price=booking.final_price,
        status=booking.status,
        payment_status=booking.payment_status,
        notes=booking.notes,
        cancellation_reason=booking.cancellation_reason,
        created_at=booking.created_at,
        car_wash_name=booking.car_wash.name if booking.car_wash else None,
        car_wash_address=booking.car_wash.address if booking.car_wash else None,
        wash_type_name=booking.wash_type.name if booking.wash_type else None,
        bay_number=booking.wash_bay.bay_number if booking.wash_bay else None,
        qr_code=qr_data,
    )


async def cancel_booking_service(
    booking_id: uuid.UUID, reason: Optional[str], session: AsyncSession
) -> dict:
    """Сервисная функция для отмены бронирования."""
    repo = BookingRepository(session)
    booking = await repo.get_by_id(booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    if booking.status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail="Нельзя отменить завершенное или уже отмененное бронирование",
        )

    # Проверка времени до начала (минимум 2 часа)
    booking_datetime = datetime.combine(booking.slot_date, booking.start_time)
    if booking_datetime < datetime.now() + timedelta(hours=2):
        raise HTTPException(
            status_code=400,
            detail="Отмена возможна не позднее чем за 2 часа до начала",
        )

    # Отменяем бронирование
    booking.status = "cancelled"
    booking.cancelled_at = datetime.now()
    booking.cancellation_reason = reason

    # Освобождаем слот
    if booking.time_slot:
        booking.time_slot.status = "available"

    await session.commit()

    # TODO: Логика возврата средств (можно вызвать другой сервис)

    return {
        "status": "cancelled",
        "booking_id": str(booking_id),
        "refund_status": "processing",
    }


async def get_carwash_bookings_service(
    carwash_id: uuid.UUID,
    date_from: Optional[date],
    date_to: Optional[date],
    status: Optional[str],
    page: int,
    per_page: int,
    session: AsyncSession,
) -> SBookingListResponse:
    """Сервисная функция для получения бронирований автомойки."""
    repo = BookingRepository(session)
    bookings, total = await repo.get_for_carwash(
        carwash_id=carwash_id,
        date_from=date_from,
        date_to=date_to,
        status=status,
        page=page,
        per_page=per_page,
    )

    items = [
        SBookingWithDetails.model_validate(b, from_attributes=True) for b in bookings
    ]

    pages = (total + per_page - 1) // per_page

    return SBookingListResponse(
        items=items, total=total, page=page, per_page=per_page, pages=pages
    )


async def start_wash_service(booking_id: uuid.UUID, session: AsyncSession) -> dict:
    """Сервисная функция для начала мойки."""
    repo = BookingRepository(session)
    booking = await repo.get_by_id(booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    if booking.status != "confirmed":
        raise HTTPException(status_code=400, detail="Бронирование не подтверждено")

    await repo.update_status(booking, "in_progress")

    return {"status": "in_progress", "booking_id": str(booking_id)}


async def complete_wash_service(booking_id: uuid.UUID, session: AsyncSession) -> dict:
    """Сервисная функция для завершения мойки."""
    repo = BookingRepository(session)
    booking = await repo.get_by_id(booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    if booking.status != "in_progress":
        raise HTTPException(status_code=400, detail="Мойка не начата")

    await repo.update_status(booking, "completed", completed_at=datetime.now())

    return {"status": "completed", "booking_id": str(booking_id)}


async def verify_qr_service(
    booking_id: uuid.UUID, qr_code: str, session: AsyncSession
) -> dict:
    """Сервисная функция для проверки QR-кода."""
    repo = BookingRepository(session)
    booking = await repo.get_by_id(booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    # Генерируем ожидаемый QR и сравниваем
    expected_qr = repo.generate_qr_data(booking.id, booking.guest_phone)

    # Простая проверка - в дальнейшем можно усилить с времеными отметками
    if qr_code != expected_qr:
        return {"valid": False, "message": "Неверный QR-код"}

    return {
        "valid": True,
        "booking": {
            "id": str(booking.id),
            "guest_name": booking.guest_name,
            "car_plate": booking.car_plate,
            "car_model": booking.car_model,
            "status": booking.status,
        },
    }
