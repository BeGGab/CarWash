import uuid
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.carwash import CarWash
from src.models.booking import Booking

from src.schemas.carwash import SCarWashCreate, SCarWashUpdate


class CarWashRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[CarWash]:
        """Получить все автомойки."""
        query = select(CarWash).order_by(CarWash.name)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, carwash_id: uuid.UUID) -> Optional[CarWash]:
        """Получить автомойку по ID."""
        return await self.session.get(CarWash, carwash_id)

    async def get_by_name(self, name: str) -> Optional[CarWash]:
        """Получить автомойку по названию."""
        query = select(CarWash).where(CarWash.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, data: SCarWashCreate) -> CarWash:
        """Создать новую автомойку."""
        carwash = CarWash(**data.model_dump())
        self.session.add(carwash)
        await self.session.commit()
        await self.session.refresh(carwash)
        return carwash

    async def update(self, carwash: CarWash, data: SCarWashUpdate) -> CarWash:
        """Обновить информацию об автомойке."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(carwash, field):
                setattr(carwash, field, value)
        await self.session.commit()
        await self.session.refresh(carwash)
        return carwash

    async def delete(self, carwash: CarWash) -> None:
        """Удалить автомойку."""
        await self.session.delete(carwash)
        await self.session.commit()

    async def get_stats(self) -> dict:
        """Получить статистику."""
        carwash_count_query = select(func.count(CarWash.id))
        carwash_count = (await self.session.execute(carwash_count_query)).scalar() or 0

        # Другую статистику можно добавить здесь, если они не связаны с бронированиями
        return {"carwash_count": carwash_count}

    async def total_bookings(self) -> dict:
        # Статистика общая , а не под пользователя
        total_bookings_query = select(func.count(Booking.id))
        total_bookings = (
            await self.session.execute(total_bookings_query)
        ).scalar() or 0
        return {"total_bookings": total_bookings}

    async def confirmed_bookings(self) -> dict:
        confirmed_bookings_query = select(func.count(Booking.id)).where(
            Booking.status == "confirmed"
        )
        confirmed_bookings = (
            await self.session.execute(confirmed_bookings_query)
        ).scalar() or 0
        return {"confirmed_bookings": confirmed_bookings}
