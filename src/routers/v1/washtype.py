"""
API роутер для работы с типами мойки
"""

import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.schemas.washtype import (
    SWashTypeCreate,
    SWashTypeUpdate,
    SWashTypeResponse,
    SWashTypeListResponse,
)
from src.services.washtype import (
    get_all_wash_types_service,
    get_wash_type_by_id_service,
    create_wash_type_service,
    update_wash_type_service,
    delete_wash_type_service,
)

router = APIRouter(prefix="/api/v1/wash-types", tags=["WashTypes"])


@router.get("/", response_model=SWashTypeListResponse)
async def get_wash_types(
    session: AsyncSession = Depends(get_async_session),
):
    """Получить все типы мойки"""
    return await get_all_wash_types_service(session)


@router.get("/{wash_type_id}", response_model=SWashTypeResponse)
async def get_wash_type(
    wash_type_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """Получить тип мойки по ID"""
    return await get_wash_type_by_id_service(wash_type_id, session)


@router.post("/", response_model=SWashTypeResponse)
async def create_wash_type(
    data: SWashTypeCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Создать тип мойки (для системных админов)"""
    return await create_wash_type_service(data, session)


@router.patch("/{wash_type_id}", response_model=SWashTypeResponse)
async def update_wash_type(
    wash_type_id: uuid.UUID,
    data: SWashTypeUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновить тип мойки"""
    return await update_wash_type_service(wash_type_id, data, session)


@router.delete("/{wash_type_id}")
async def delete_wash_type(
    wash_type_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """Удалить тип мойки"""
    return await delete_wash_type_service(wash_type_id, session)
