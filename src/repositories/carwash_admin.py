import uuid
from typing import List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.carwash_admin import CarWashAdmin
from src.schemas.carwash_admin import SCarWashAdminCreate




class CarWashAdminRepository:
    model = CarWashAdmin

    async def add(self, session: AsyncSession, data: SCarWashAdminCreate) -> CarWashAdmin:
        new_admin = self.model(**data.model_dump())
        session.add(new_admin)
        await session.flush()
        return new_admin

    async def get_by_id(
        self, session: AsyncSession, admin_id: uuid.UUID
    ) -> CarWashAdmin | None:
        return await session.get(self.model, admin_id)

    async def get_by_user_and_carwash(
        self, session: AsyncSession, user_id: int, car_wash_id: uuid.UUID
    ) -> CarWashAdmin | None:
        query = select(self.model).where(
            and_(self.model.user_id == user_id, self.model.car_wash_id == car_wash_id)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_admin_roles(self, session: AsyncSession, user_id: int) -> list[CarWashAdmin]:
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .options(selectinload(self.model.car_wash))
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def get_by_carwash_id(
        self, session: AsyncSession, car_wash_id: uuid.UUID
    ) -> list[CarWashAdmin]:
        query = (
            select(self.model)
            .where(self.model.car_wash_id == car_wash_id)
            .options(selectinload(self.model.user))
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def delete(self, session: AsyncSession, admin: CarWashAdmin) -> None:
        await session.delete(admin)
        await session.flush()
