from typing import List, Optional
from sqlalchemy import select
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
