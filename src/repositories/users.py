from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User


class UserRepository:
    model = User

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_one_or_none(self, **filter_by) -> Optional[User]:
        query = select(User).options(selectinload(User.bookings)).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100, **filter_by) -> List[User]:
        query = (
            select(User)
            .options(selectinload(User.bookings))
            .filter_by(**filter_by)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def find_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        return await self.get_one_or_none(telegram_id=telegram_id)

    async def find_by_phone(self, phone: str) -> Optional[User]:
        return await self.get_one_or_none(phone_number=phone)

    async def find_by_id_or_telegram_id(self, user_id: int | str) -> Optional[User]:
        query = select(User).where(
            or_(User.id == user_id, User.telegram_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
