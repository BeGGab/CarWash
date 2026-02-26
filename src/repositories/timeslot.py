"""
Репозиторий для работы с временными слотами.
"""

import uuid
from typing import List, Dict, Any
from datetime import date

from sqlalchemy import select, func, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.timeslot import TimeSlot


class TimeSlotRepository:
    model = TimeSlot

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def count_available_slots(self, carwash_id: uuid.UUID, on_date: date) -> int:
        """Подсчитывает количество свободных слотов для автомойки на указанную дату."""
        query = select(func.count(self.model.id)).where(
            self.model.car_wash_id == carwash_id,
            self.model.slot_date == on_date,
            self.model.status == "available",
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def bulk_create(self, slots_data: List[Dict[str, Any]]):
        """Выполняет массовое создание слотов."""
        if not slots_data:
            return
        query = insert(self.model).values(slots_data)
        await self.session.execute(query)
