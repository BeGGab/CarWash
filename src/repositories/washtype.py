"""
Репозиторий для работы с типами мойки
"""
import uuid
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.washtype import WashType
from src.schemas.washtype import SWashTypeCreate, SWashTypeUpdate


class WashTypeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> tuple[List[WashType], int]:
        """Получить все типы мойки и их общее количество."""
        query = select(WashType).order_by(WashType.base_price)
        result = await self.session.execute(query)
        wash_types = result.scalars().all()

        count_query = select(func.count(WashType.id))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        return wash_types, total

    async def get_by_id(self, wash_type_id: uuid.UUID) -> Optional[WashType]:
        """Получить тип мойки по ID."""
        return await self.session.get(WashType, wash_type_id)

    async def create(self, data: SWashTypeCreate) -> WashType:
        """Создать новый тип мойки."""
        wash_type = WashType(**data.model_dump())
        self.session.add(wash_type)
        await self.session.commit()
        await self.session.refresh(wash_type)
        return wash_type

    async def update(
        self, wash_type: WashType, data: SWashTypeUpdate
    ) -> WashType:
        """Обновить тип мойки."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(wash_type, field, value)
        await self.session.commit()
        await self.session.refresh(wash_type)
        return wash_type

    async def delete(self, wash_type: WashType) -> None:
        """Удалить тип мойки."""
        await self.session.delete(wash_type)
        await self.session.commit()
