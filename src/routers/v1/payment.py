"""
API роутер для работы с платежами
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.schemas.payment import (
    SPaymentCreate,
    SPaymentResponse,
    SRefundRequest,
    SRefundResponse,
)
from src.services.payment_gateway import PaymentGatewayService, get_payment_gateway
from src.services.payment import (
    create_payment_service,
    process_webhook_service,
    create_refund_service,
    confirm_demo_payment_service,
)

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])


# ==================== Эндпоинты ====================

@router.post("/create", response_model=SPaymentResponse)
async def create_payment(
    data: SPaymentCreate,
    gateway: PaymentGatewayService = Depends(get_payment_gateway),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Создать платеж для бронирования
    
    Возвращает URL для перенаправления на страницу оплаты
    """
    return await create_payment_service(data, gateway, session)


@router.get("/status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    gateway: PaymentGatewayService = Depends(get_payment_gateway),
):
    """Получить статус платежа"""
    payment_data = await gateway.get_payment(payment_id)
    return {
        "payment_id": payment_id,
        "status": payment_data["status"],
        "paid": payment_data.get("paid", False)
    }


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    gateway: PaymentGatewayService = Depends(get_payment_gateway),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Webhook для получения уведомлений от платежной системы
    
    Обрабатывает события:
    - payment.succeeded - платеж успешен
    - payment.canceled - платеж отменен
    - refund.succeeded - возврат выполнен
    """
    return await process_webhook_service(request, gateway, session)


@router.post("/refund", response_model=SRefundResponse)
async def create_refund(
    data: SRefundRequest,
    gateway: PaymentGatewayService = Depends(get_payment_gateway),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Создать запрос на возврат средств
    
    - Полный возврат при отмене за 2+ часа до начала
    - Частичный возврат при отмене за 1-2 часа (50%)
    - Без возврата при отмене менее чем за 1 час
    """
    return await create_refund_service(data, gateway, session)


# ==================== Демо-эндпоинт для тестирования ====================

@router.get("/demo-pay")
async def demo_payment_page(payment_id: str = Query(...), amount: float = Query(...)):
    """
    Демо-страница оплаты для тестирования
    
    В продакшене это будет страница ЮKassa
    """
    return {
        "message": "Демо-страница оплаты",
        "payment_id": payment_id,
        "amount": amount,
        "instructions": "Для подтверждения оплаты вызовите POST /api/v1/payments/demo-confirm",
        "confirm_url": f"/api/v1/payments/demo-confirm?payment_id={payment_id}"
    }


@router.post("/demo-confirm")
async def demo_confirm_payment(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Демо-подтверждение платежа
    
    Эмулирует успешный webhook от ЮKassa
    """
    return await confirm_demo_payment_service(session)
