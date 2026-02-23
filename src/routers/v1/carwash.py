import uuid
from typing import List, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session

from src.schemas.carwash import SCarWashCreate, SCarWashResponse, SCarWashUpdate

from src.services.carwash import (
    get_all_carwashes_service,
    create_carwash_service,
    delete_carwash_service,
    get_carwash_by_id_service,
    get_statistics_service,
    update_carwash_service,
)

router = APIRouter(prefix="/api/v1/carwashes", tags=["CarWashes"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_carwashes(
    session: AsyncSession = Depends(get_async_session),
) -> List[SCarWashResponse]:
    """Получить список всех автомоек."""
    return await get_all_carwashes_service(session)


@router.get("/statistics", status_code=status.HTTP_200_OK)
async def get_statistics(session: AsyncSession = Depends(get_async_session)) -> Dict:
    """Получить общую статистику по системе (для админов)."""
    return await get_statistics_service(session)


@router.get("/{carwash_id}", status_code=status.HTTP_200_OK)
async def get_carwash_by_id(
    carwash_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
) -> SCarWashResponse:
    """Получить детальную информацию об автомойке по ID."""
    return await get_carwash_by_id_service(carwash_id, session)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_carwash(
    data: SCarWashCreate, session: AsyncSession = Depends(get_async_session)
) -> SCarWashResponse:
    """Создать новую автомойку (для админов)."""
    return await create_carwash_service(data, session)


@router.put("/{carwash_id}", status_code=status.HTTP_200_OK)
async def update_carwash(
    carwash_id: uuid.UUID,
    data: SCarWashUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> SCarWashResponse:
    """Обновить информацию об автомойке (для админов)."""
    return await update_carwash_service(carwash_id, data, session)


@router.delete("/{carwash_id}", status_code=status.HTTP_200_OK)
async def delete_carwash(
    carwash_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
):
    """Удалить автомойку (для админов)."""
    return await delete_carwash_service(carwash_id, session)
