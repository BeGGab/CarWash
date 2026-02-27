"""
API эндпоинты для работы с автомойками.
"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.schemas.carwash import SCarWashResponse
from src.services.carwash import (
    get_all_carwashes_service,
    get_carwash_by_id_service,
    get_carwash_slots_stats_service,
)

router = APIRouter(prefix="/api/v1/carwashes", tags=["CarWashes"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_carwashes(
    session: AsyncSession = Depends(get_async_session),
) -> List[SCarWashResponse]:
    """Получение списка всех автомоек."""
    return await get_all_carwashes_service(session)


@router.get("/{carwash_id}", status_code=status.HTTP_200_OK)
async def get_carwash_by_id(
    carwash_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
) -> SCarWashResponse:
    """Получение информации об одной автомойке по ID."""
    return await get_carwash_by_id_service(carwash_id, session)


@router.get(
    "/{carwash_id}/slots-count", response_model=dict, status_code=status.HTTP_200_OK
)
async def get_carwash_slots_stats(
    carwash_id: uuid.UUID,
    date: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение количества свободных слотов для автомойки на дату."""
    return await get_carwash_slots_stats_service(carwash_id, date, session)
