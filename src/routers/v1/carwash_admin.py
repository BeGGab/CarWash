# d:\carwash\src\routers\v1\carwash_admin.py
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.services.carwash_admin import CarWashAdminService
from src.schemas.carwash_admin import (
    SCarWashAdmin,
    SCarWashAdminResponse,
)

router = APIRouter(prefix="/admin/carwash-admins", tags=["Admin: CarWash Admins"])


@router.post("/", response_model=SCarWashAdmin, status_code=status.HTTP_201_CREATED)
async def add_carwash_admin(
    car_wash_id: uuid.UUID = Body(...),
    phone_number: str = Body(...),
    session: AsyncSession = Depends(get_async_session),
):
    """Назначает пользователя администратором автомойки по номеру телефона."""
    service = CarWashAdminService(session)
    try:
        new_admin = await service.add_admin(car_wash_id, phone_number)
        return new_admin
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/by-carwash/{car_wash_id}", response_model=List[SCarWashAdminResponse]
)
async def get_carwash_admins(
    car_wash_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение списка администраторов для конкретной автомойки."""
    service = CarWashAdminService(session)
    admins = await service.get_admins_by_carwash(car_wash_id)
    return admins


@router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_carwash_admin(
    admin_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
):
    """Удаление администратора автомойки."""
    service = CarWashAdminService(session)
    try:
        await service.delete_admin(admin_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
