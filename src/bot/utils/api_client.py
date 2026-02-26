"""
Асинхронный клиент для взаимодействия с API CarWash.
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx

from src.core.config import Settings


logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._client = httpx.AsyncClient(base_url=self._base_url)

    async def close(self):
        await self._client.aclose()

    async def _request(self, method: str, url: str, **kwargs) -> Any:
        """Универсальный метод для выполнения запросов."""
        try:
            response = await self._client.request(method, url, **kwargs)
            response.raise_for_status()
            if response.status_code == 204:  # No Content
                return None
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"API error on {method} {url}: {e.response.status_code} - {e.response.text}"
            )
            # Перевыбрасываем исключение, чтобы его можно было обработать в хендлере
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error on {method} {url}: {e}")
            raise

    # CarWash Endpoints
    async def get_carwash(self, carwash_id: str | UUID) -> Dict[str, Any]:
        return await self._request(
            "GET", f"/api/v1/carwashes/{carwash_id}"
        )  # Public endpoint

    async def get_carwashes(
        self, latitude: Optional[float] = None, longitude: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        params = {}
        if latitude is not None and longitude is not None:
            params = {"latitude": latitude, "longitude": longitude}
        return await self._request(
            "GET", "/api/v1/carwashes/", params=params
        )  # Public endpoint

    async def create_carwash(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "/api/v1/admin/system/carwashes", json=data)

    async def delete_carwash(self, carwash_id: str | UUID) -> None:
        await self._request("DELETE", f"/api/v1/admin/system/carwashes/{carwash_id}")

    async def get_system_stats(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/v1/admin/system/statistics")

    async def get_slots_count(
        self, carwash_id: str | UUID, date: Optional[str] = None
    ) -> Dict[str, Any]:
        params = {"date": date} if date else {}
        return await self._request(
            "GET", f"/api/v1/carwashes/{carwash_id}/slots-count", params=params
        )

    # TimeSlot Endpoints
    async def get_time_slots(
        self, carwash_id: str | UUID, date: str
    ) -> List[Dict[str, Any]]:
        params = {"date": date}
        return await self._request(
            "GET", f"/api/v1/carwashes/{carwash_id}/slots", params=params
        )

    # WashType Endpoints
    async def get_wash_types(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/v1/wash-types/")

    # Booking Endpoints
    async def calculate_price(
        self, time_slot_id: str, wash_type_id: str
    ) -> Dict[str, Any]:
        payload = {"time_slot_id": time_slot_id, "wash_type_id": wash_type_id}
        return await self._request(
            "POST", "/api/v1/bookings/calculate-price", json=payload
        )

    async def create_booking(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "/api/v1/bookings/create", json=payload)

    async def get_my_bookings(self, phone: str) -> Dict[str, Any]:
        params = {"phone": phone}
        return await self._request("GET", "/api/v1/bookings/my", params=params)

    async def get_booking_details(self, booking_id: str | UUID) -> Dict[str, Any]:
        return await self._request("GET", f"/api/v1/bookings/{booking_id}")

    async def cancel_booking(self, booking_id: str | UUID) -> Dict[str, Any]:
        payload = {"reason": "Отменено пользователем в боте"}
        return await self._request(
            "POST", f"/api/v1/bookings/{booking_id}/cancel", json=payload
        )

    # CarWash Admin Endpoints
    async def get_carwash_bookings(
        self, carwash_id: str | UUID, **params
    ) -> Dict[str, Any]:
        return await self._request(
            "GET", f"/api/v1/admin/carwash/{carwash_id}/bookings", params=params
        )

    async def verify_qr_code(
        self, booking_id: str | UUID, qr_code: str
    ) -> Dict[str, Any]:
        params = {"qr_code": qr_code}
        return await self._request(
            "POST",
            f"/api/v1/admin/carwash/bookings/{booking_id}/verify-qr",
            params=params,
        )

    async def start_wash(self, booking_id: str | UUID) -> Dict[str, Any]:
        return await self._request(
            "POST", f"/api/v1/admin/carwash/bookings/{booking_id}/start"
        )

    async def complete_wash(self, booking_id: str | UUID) -> Dict[str, Any]:
        return await self._request(
            "POST", f"/api/v1/admin/carwash/bookings/{booking_id}/complete"
        )


def get_api_client(settings: Settings) -> ApiClient:
    """DI-фабрика для создания экземпляра ApiClient."""
    return ApiClient(base_url=settings.api_base_url)
