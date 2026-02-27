import uuid
import logging
from typing import List
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from src.models.carwash_admin import CarWashAdmin
from src.repositories.carwash_admin import CarWashAdminRepository
from src.repositories.users import UserRepository
from src.schemas.users import (
    SUserCreate,
    SUserUpdate,
    SUserResponse,
    SPhoneVerification,
)
from src.repositories.booking import BookingRepository

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session
        self.user_repo = UserRepository(session)
        self.booking_repo = BookingRepository(session)
        self.carwash_admin_repo = CarWashAdminRepository() # No session needed for its methods

    async def create_user(self, user_data: SUserCreate) -> SUserResponse:
        existing_user = await self.user_repo.get_one_or_none(
            telegram_id=int(user_data.telegram_id)
        )
        if existing_user:
            logger.warning(
                f"Попытка создать уже существующего пользователя: {user_data.telegram_id}"
            )
            return await self.find_user(telegram_id=int(user_data.telegram_id))

        new_user_orm = self.user_repo.model(**user_data.model_dump())
        self.session.add(new_user_orm)
        await self.session.flush()
        await self.session.refresh(new_user_orm)
        logger.info(f"Создан новый пользователь: {new_user_orm.telegram_id}")

        return await self.find_user(telegram_id=new_user_orm.telegram_id)

    async def verify_user(self, data: SPhoneVerification):
        user = await self.user_repo.get_one_or_none(telegram_id=data.telegram_id)
        if not user:
            logger.error(f"Пользователь не найден: {data}")
            raise HTTPException(detail="Пользователь не найден", status_code=404)
        user.phone_number = data.phone_number
        user.is_verified = True
        await self.session.flush()
        return await self.find_user(telegram_id=data.telegram_id)

    async def find_user(self, **filter_by) -> SUserResponse:
        user = await self.user_repo.get_one_or_none(**filter_by)
        if not user:
            logger.error(f"Пользователь не найден: {filter_by}")
            raise HTTPException(detail="Пользователь не найден", status_code=404)
        total_booking = await self.booking_repo.statistic_total(user.id)
        completed_booking = await self.booking_repo.statistic_completed(user.id)

        # Собираем ответ, включая статистику
        user_data_dict = user.__dict__
        user_data_dict["total_bookings"] = total_booking
        user_data_dict["completed_bookings"] = completed_booking

        return SUserResponse.model_validate(user_data_dict)

    async def find_all_users(
        self, skip: int = 0, limit: int = 100, **filter_by
    ) -> List[SUserResponse]:
        users = await self.user_repo.get_all(skip, limit, **filter_by)
        if not users:
            logger.error(f"Пользователи не найдены: {filter_by}")
            raise HTTPException(detail="Пользователи не найдены", status_code=404)
        return [SUserResponse.model_validate(user) for user in users]

    async def update_user(self, data: SUserUpdate) -> SUserResponse:
        user = await self.user_repo.get_one_or_none(telegram_id=data.telegram_id)
        if not user:
            logger.error(f"Пользователь не найден: {data.telegram_id}")
            raise HTTPException(detail="Пользователь не найден", status_code=404)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return SUserResponse.model_validate(user)

    async def delete_user(self, user_id: uuid.UUID):
        user = await self.user_repo.get_one_or_none(id=user_id)
        if not user:
            logger.error(f"Пользователь не найден: {user_id}")
            raise HTTPException(detail="Пользователь не найден", status_code=404)
        await self.session.delete(user)

    async def get_for_admins(self, **filter_by) -> SUserResponse:
        user = await self.user_repo.get_one_or_none(**filter_by)
        if not user:
            logger.error(f"Пользователь не найден: {filter_by}")
            raise HTTPException(detail="Пользователь не найден", status_code=404)
        return SUserResponse.model_validate(user)

    async def get_user_carwash_admin_roles(self, user_id: int) -> list[CarWashAdmin]:
        user = await self.user_repo.find_by_telegram_id(user_id)
        if not user:
            return []
        return await self.carwash_admin_repo.get_user_admin_roles(self.session, user.id)
