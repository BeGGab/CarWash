import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from src.repositories.carwash_admin import CarWashAdminRepository
from src.repositories.users import UserRepository
from src.schemas.carwash_admin import SCarWashAdmin, SCarWashAdminCreate
from src.models.carwash_admin import CarWashAdmin


class CarWashAdminService:
    def __init__(
        self,
        session: AsyncSession,
        repo: CarWashAdminRepository = None,
        user_repo: UserRepository = None,
        
    ):
        self.session = session
        self.repo = repo
        self.user_repo = user_repo

    async def add_admin(
        self, car_wash_id: uuid.UUID, phone_number: str
    ) -> CarWashAdmin:
        user = await self.user_repo.find_by_phone(phone_number)
        if not user:
            raise ValueError("Пользователь с таким номером телефона не найден.")

        existing = await self.repo.get_by_user_and_carwash(
            self.session, user.id, car_wash_id
        )
        if existing:
            raise ValueError("Этот пользователь уже является администратором этой мойки.")

        admin_data = SCarWashAdminCreate(user_id=user.id, car_wash_id=car_wash_id)
        new_admin = await self.repo.add(self.session, admin_data)
        return new_admin

    async def get_admins_by_carwash(
        self, car_wash_id: uuid.UUID
    ) -> list[CarWashAdmin]:
        return await self.repo.get_by_carwash_id(self.session, car_wash_id)

    async def delete_admin(self, admin_id: uuid.UUID) -> None:
        admin = await self.repo.get_by_id(self.session, admin_id)
        if not admin:
            raise ValueError("Администратор не найден.")

        await self.repo.delete(self.session, admin)
        return None

    async def get_user_admin_roles(self, user_id: uuid.UUID) -> list[CarWashAdmin]:
        """Получает список автомоек, где пользователь является администратором."""
        return await self.repo.get_user_admin_roles(self.session, user_id)
