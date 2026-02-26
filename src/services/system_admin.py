"""
API эндпоинты для системных администраторов.
"""

import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.schemas.carwash import SCarWashCreate, SCarWashResponse, SCarWashUpdate
from src.schemas.washbay import SWashBayCreate, SWashBayResponse
from src.services.carwash import (
    create_carwash_service,
    update_carwash_service,
    delete_carwash_service,
    get_statistics_service,
    add_wash_bay_service,
)

router = APIRouter(prefix="/admin/system", tags=["Admin: System"])


@router.post(
    "/carwashes", response_model=SCarWashResponse, status_code=status.HTTP_201_CREATED
)
async def create_carwash(
    carwash_data: SCarWashCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Создание новой автомойки."""
    return await create_carwash_service(carwash_data, session)


@router.patch("/carwashes/{carwash_id}", response_model=SCarWashResponse)
async def update_carwash(
    carwash_id: uuid.UUID,
    carwash_data: SCarWashUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновление информации об автомойке."""
    return await update_carwash_service(carwash_id, carwash_data, session)


@router.delete("/carwashes/{carwash_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_carwash(
    carwash_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаление автомойки."""
    await delete_carwash_service(carwash_id, session)


@router.post(
    "/carwashes/{carwash_id}/bays",
    response_model=SWashBayResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_wash_bay(
    carwash_id: uuid.UUID,
    bay_data: SWashBayCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Добавление моечного бокса к автомойке и генерация слотов."""
    return await add_wash_bay_service(carwash_id, bay_data, session)


@router.get("/statistics", response_model=dict)
async def get_system_statistics(session: AsyncSession = Depends(get_async_session)):
    """Получение общей статистики по системе."""
    return await get_statistics_service(session)
