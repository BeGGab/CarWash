"""
Сервисный слой для работы с платежами.
"""
import uuid
from typing import Optional
from datetime import datetime

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.booking import BookingRepository
from src.services.payment_gateway import PaymentGatewayService
from src.schemas.payment import (
    SPaymentCreate,
    SPaymentResponse,
    SRefundRequest,
    SRefundResponse,
)


async def create_payment_service(
    data: SPaymentCreate,
    gateway: PaymentGatewayService,
    session: AsyncSession,
) -> SPaymentResponse:
    """Сервис для создания платежа."""
    repo = BookingRepository(session)
    booking = await repo.get_by_id(data.booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    if booking.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Бронирование уже оплачено")

    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Бронирование отменено")

    prepayment_amount = round(booking.final_price * 0.5, 2)
    description = f"Предоплата за мойку в {booking.car_wash.name if booking.car_wash else 'автомойке'}"

    payment_data = await gateway.create_payment(
        booking_id=booking.id,
        amount=prepayment_amount,
        description=description,
        return_url=data.return_url,
        metadata={
            "car_wash_id": str(booking.car_wash_id),
            "slot_date": booking.slot_date.isoformat(),
            "prepayment": True,
        },
    )

    # Сохраняем ID платежа в бронировании
    await repo.update_payment_info(booking, payment_id=payment_data["id"])

    return SPaymentResponse(
        payment_id=payment_data["id"],
        booking_id=booking.id,
        amount=prepayment_amount,
        status=payment_data["status"],
        confirmation_url=payment_data["confirmation"]["confirmation_url"],
        created_at=datetime.now(),
    )


async def process_webhook_service(
    request: Request, gateway: PaymentGatewayService, session: AsyncSession
) -> dict:
    """Сервис для обработки webhook от платежной системы."""
    body = await request.body()
    signature = request.headers.get("X-Signature", "")
    # Если провайдер не прислал подпись — считаем, что это демо-режим и не блокируем запрос.
    # В проде нужно гарантировать наличие подписи и выбрасывать ошибку.
    if signature and not gateway.verify_signature(body, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    data = await request.json()
    event = data.get("event")
    payment_object = data.get("object", {})
    booking_id_str = payment_object.get("metadata", {}).get("booking_id")

    if not booking_id_str:
        return {"status": "ignored", "reason": "no booking_id in metadata"}

    repo = BookingRepository(session)
    try:
        booking = await repo.get_by_id(uuid.UUID(booking_id_str))
    except ValueError:
        return {"status": "ignored", "reason": "invalid booking_id format"}

    if not booking:
        return {"status": "ignored", "reason": "booking not found"}

    if event == "payment.succeeded":
        booking.payment_status = "paid"
        booking.status = "confirmed"
        if booking.time_slot:
            booking.time_slot.status = "booked"
        await session.commit()
        # TODO: Отправить уведомление пользователю и автомойке
        return {"status": "processed", "booking_status": "confirmed"}

    elif event == "payment.canceled":
        booking.payment_status = "failed"
        booking.status = "cancelled"
        booking.cancellation_reason = "Платеж отменен"
        if booking.time_slot:
            booking.time_slot.status = "available"
        await session.commit()
        return {"status": "processed", "booking_status": "cancelled"}

    elif event == "refund.succeeded":
        booking.payment_status = "refunded"
        await session.commit()
        return {"status": "processed", "payment_status": "refunded"}

    return {"status": "ignored", "reason": "unknown event"}


async def create_refund_service(
    data: SRefundRequest, gateway: PaymentGatewayService, session: AsyncSession
) -> SRefundResponse:
    """Сервис для создания возврата."""
    repo = BookingRepository(session)
    booking = await repo.get_by_id(data.booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    if booking.payment_status != "paid":
        raise HTTPException(status_code=400, detail="Бронирование не оплачено")

    if not booking.payment_id:
        raise HTTPException(
            status_code=400, detail="Отсутствует ID платежа для возврата"
        )

    prepayment_amount = round(booking.final_price * 0.5, 2)
    refund_amount = data.amount if data.amount is not None else prepayment_amount

    if refund_amount > prepayment_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Сумма возврата не может превышать {prepayment_amount} руб.",
        )

    refund_data = await gateway.create_refund(
        payment_id=booking.payment_id, amount=refund_amount, reason=data.reason
    )

    return SRefundResponse(
        refund_id=refund_data["id"],
        booking_id=booking.id,
        amount=refund_amount,
        status=refund_data["status"],
        created_at=datetime.now(),
    )


async def confirm_demo_payment_service(session: AsyncSession) -> dict:
    """Сервис для демо-подтверждения платежа."""
    repo = BookingRepository(session)
    booking = await repo.find_pending_payment()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование для оплаты не найдено")

    booking.payment_status = "paid"
    booking.status = "confirmed"
    if booking.time_slot:
        booking.time_slot.status = "booked"
    await session.commit()

    return {
        "status": "success",
        "message": "Платеж подтвержден",
        "booking_id": str(booking.id),
        "booking_status": "confirmed",
    }
