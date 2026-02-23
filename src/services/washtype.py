"""
Сервисный слой для работы с типами мойки
"""
import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.washtype import WashTypeRepository
from src.schemas.washtype import (
    SWashTypeCreate,
    SWashTypeUpdate,
    SWashTypeResponse,
    SWashTypeListResponse,
)


async def get_all_wash_types_service(
    session: AsyncSession,
) -> SWashTypeListResponse:
    """Сервис для получения всех типов мойки."""
    repo = WashTypeRepository(session)
    wash_types, total = await repo.get_all()
    return SWashTypeListResponse(
        items=[SWashTypeResponse.model_validate(wt) for wt in wash_types],
        total=total,
    )


async def get_wash_type_by_id_service(
    wash_type_id: uuid.UUID, session: AsyncSession
) -> SWashTypeResponse:
    """Сервис для получения одного типа мойки по ID."""
    repo = WashTypeRepository(session)
    wash_type = await repo.get_by_id(wash_type_id)
    if not wash_type:
        raise HTTPException(status_code=404, detail="Тип мойки не найден")
    return SWashTypeResponse.model_validate(wash_type)


async def create_wash_type_service(
    data: SWashTypeCreate, session: AsyncSession
) -> SWashTypeResponse:
    """Сервис для создания типа мойки."""
    repo = WashTypeRepository(session)
    wash_type = await repo.create(data)
    return SWashTypeResponse.model_validate(wash_type)


async def update_wash_type_service(
    wash_type_id: uuid.UUID, data: SWashTypeUpdate, session: AsyncSession
) -> SWashTypeResponse:
    """Сервис для обновления типа мойки."""
    repo = WashTypeRepository(session)
    wash_type = await repo.get_by_id(wash_type_id)
    if not wash_type:
        raise HTTPException(status_code=404, detail="Тип мойки не найден")
    updated_wash_type = await repo.update(wash_type, data)
    return SWashTypeResponse.model_validate(updated_wash_type)


async def delete_wash_type_service(
    wash_type_id: uuid.UUID, session: AsyncSession
) -> dict:
    """Сервис для удаления типа мойки."""
    repo = WashTypeRepository(session)
    wash_type = await repo.get_by_id(wash_type_id)
    if not wash_type:
        raise HTTPException(status_code=404, detail="Тип мойки не найден")
    await repo.delete(wash_type)
    return {"status": "deleted", "id": str(wash_type_id)}
