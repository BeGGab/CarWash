"""
Сервис-шлюз для интеграции с внешней платежной системой (например, ЮKassa).
В данном проекте используется заглушка для демонстрации.
"""
import uuid
import hashlib
import hmac
from datetime import datetime
from typing import Optional


class PaymentGatewayService:
    """
    Сервис интеграции с платежной системой.
    В продакшене здесь будет реальная интеграция с ЮKassa/Stripe/Т-Касса.
    """

    def __init__(self, shop_id: str = None, secret_key: str = None):
        self.shop_id = shop_id or "demo_shop"
        self.secret_key = secret_key or "demo_secret"
        self.base_url = "https://api.yookassa.ru/v3"

    async def create_payment(
        self,
        booking_id: uuid.UUID,
        amount: float,
        description: str,
        return_url: str,
        metadata: dict = None,
    ) -> dict:
        """
        Создать платеж в ЮKassa.
        В демо-режиме возвращает заглушку.
        """
        payment_id = f"pay_{uuid.uuid4().hex[:16]}"

        # В реальной интеграции здесь будет асинхронный HTTP-запрос к API ЮKassa

        return {
            "id": payment_id,
            "status": "pending",
            "amount": {"value": str(amount), "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "confirmation_url": f"/api/v1/payments/demo-pay?payment_id={payment_id}&amount={amount}",
            },
            "created_at": datetime.now().isoformat(),
            "metadata": {"booking_id": str(booking_id)},
        }

    async def get_payment(self, payment_id: str) -> dict:
        """Получить информацию о платеже."""
        return {"id": payment_id, "status": "succeeded", "paid": True}

    async def create_refund(
        self, payment_id: str, amount: float, reason: Optional[str] = None
    ) -> dict:
        """Создать возврат."""
        refund_id = f"ref_{uuid.uuid4().hex[:16]}"

        return {
            "id": refund_id,
            "payment_id": payment_id,
            "status": "succeeded",
            "amount": {"value": str(amount), "currency": "RUB"},
            "created_at": datetime.now().isoformat(),
        }

    def verify_signature(self, body: bytes, signature: str) -> bool:
        """Проверить подпись webhook."""
        expected = hmac.new(
            self.secret_key.encode(), body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)


def get_payment_gateway() -> PaymentGatewayService:
    """
    DI-функция для получения экземпляра сервиса платежного шлюза.
    Здесь можно будет передавать настройки из Settings.
    """
    return PaymentGatewayService()
