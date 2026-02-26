"""
Сервисный слой для работы с автомойками
"""

import uuid
from typing import List, Optional
from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.carwash import CarWashRepository
from src.repositories.timeslot import TimeSlotRepository
from src.services.timeslot import generate_slots_for_bay_service

from src.schemas.carwash import SCarWashCreate, SCarWashResponse, SCarWashUpdate
from src.schemas.washbay import SWashBayCreate, SWashBayResponse


async def get_all_carwashes_service(session: AsyncSession) -> List[SCarWashResponse]:
    repo = CarWashRepository(session)
    carwashes = await repo.get_all()
    return [SCarWashResponse.model_validate(cw) for cw in carwashes]


async def get_carwash_by_id_service(
    carwash_id: uuid.UUID, session: AsyncSession
) -> SCarWashResponse:
    repo = CarWashRepository(session)
    carwash = await repo.get_by_id(carwash_id)
    if not carwash:
        raise HTTPException(status_code=404, detail="Автомойка не найдена")
    return SCarWashResponse.model_validate(carwash)


async def create_carwash_service(
    data: SCarWashCreate, session: AsyncSession
) -> SCarWashResponse:
    repo = CarWashRepository(session)
    existing_carwash = await repo.get_by_name(data.name)
    if existing_carwash:
        raise HTTPException(
            status_code=400, detail="Автомойка с таким названием уже существует"
        )

    carwash = await repo.create(data)
    # Логика создания слотов перенесена в сервис добавления моечного бокса,
    # так как слоты привязаны к боксам.
    return SCarWashResponse.model_validate(carwash)


async def add_wash_bay_service(
    carwash_id: uuid.UUID, data: SWashBayCreate, session: AsyncSession
) -> SWashBayResponse:
    """Сервис для добавления моечного бокса и запуска генерации слотов."""
    repo = CarWashRepository(session)
    wash_bay = await repo.add_bay(carwash_id, data)

    # Запускаем генерацию слотов для нового бокса
    await generate_slots_for_bay_service(carwash_id, wash_bay, session)

    return SWashBayResponse.model_validate(wash_bay)


async def update_carwash_service(
    carwash_id: uuid.UUID, data: SCarWashUpdate, session: AsyncSession
) -> SCarWashResponse:
    """Сервис для обновления информации об автомойке."""
    repo = CarWashRepository(session)
    carwash_to_update = await repo.get_by_id(carwash_id)
    if not carwash_to_update:
        raise HTTPException(status_code=404, detail="Автомойка не найдена")

    updated_carwash = await repo.update(carwash_to_update, data)
    return SCarWashResponse.model_validate(updated_carwash)


async def delete_carwash_service(carwash_id: uuid.UUID, session: AsyncSession) -> dict:
    repo = CarWashRepository(session)
    carwash = await repo.get_by_id(carwash_id)
    if not carwash:
        raise HTTPException(status_code=404, detail="Автомойка не найдена")
    await repo.delete(carwash)
    return {"status": "deleted", "id": str(carwash_id)}


async def get_statistics_service(session: AsyncSession) -> dict:
    carwash_repo = CarWashRepository(session)
    carwash_count = (await carwash_repo.get_stats())["carwash_count"]

    total = await carwash_repo.total_bookings()
    total_bookings = total["total_bookings"]

    confirmed = await carwash_repo.confirmed_bookings()
    confirmed_bookings = confirmed["confirmed_bookings"]

    return {
        "carwashes_count": carwash_count,
        "total_bookings": total_bookings,
        "confirmed_bookings": confirmed_bookings,
    }


async def get_carwash_slots_stats_service(
    carwash_id: uuid.UUID, on_date_str: Optional[str], session: AsyncSession
) -> dict:
    """Сервис для получения количества свободных слотов."""
    repo = TimeSlotRepository(session)
    on_date = date.fromisoformat(on_date_str) if on_date_str else date.today()

    count = await repo.count_available_slots(carwash_id=carwash_id, on_date=on_date)

    return {"available_slots_count": count, "date": on_date.isoformat()}
