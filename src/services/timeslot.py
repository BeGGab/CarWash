"""
Сервисный слой для работы с временными слотами.
"""

import uuid
from datetime import date, time, timedelta, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.timeslot import TimeSlotRepository
from src.repositories.carwash import CarWashRepository
from src.models.washbay import WashBay


async def generate_slots_for_bay_service(
    carwash_id: uuid.UUID,
    wash_bay: WashBay,
    session: AsyncSession,
    days_ahead: int = 30,
    slot_duration_minutes: int = 30,
):
    """
    Генерирует временные слоты для одного моечного бокса на N дней вперед.

    :param carwash_id: ID автомойки.
    :param wash_bay: Объект моечного бокса.
    :param session: Сессия базы данных.
    :param days_ahead: Количество дней для генерации.
    :param slot_duration_minutes: Длительность одного слота в минутах.
    """
    carwash_repo = CarWashRepository(session)
    timeslot_repo = TimeSlotRepository(session)

    carwash = await carwash_repo.get_by_id(carwash_id)
    if not carwash:
        # В реальном приложении здесь лучше выбрасывать исключение
        return

    start_time: time = carwash.working_hours["start"]
    end_time: time = carwash.working_hours["end"]

    slots_to_create = []
    today = date.today()

    for day_offset in range(days_ahead):
        current_date = today + timedelta(days=day_offset)
        slot_time = datetime.combine(current_date, start_time)
        end_datetime = datetime.combine(current_date, end_time)

        while slot_time < end_datetime:
            slots_to_create.append(
                {
                    "car_wash_id": carwash_id,
                    "wash_bay_id": wash_bay.id,
                    "slot_date": current_date,
                    "start_time": slot_time.time(),
                    "end_time": (
                        slot_time + timedelta(minutes=slot_duration_minutes)
                    ).time(),
                    "status": "available",
                }
            )
            slot_time += timedelta(minutes=slot_duration_minutes)

    await timeslot_repo.bulk_create(slots_to_create)
