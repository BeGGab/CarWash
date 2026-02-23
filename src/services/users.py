import uuid
import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


from src.schemas.users import SUserCreate, SUserUpdate, SUserResponse, SPhoneVerification

from src.repositories.users import UserRepository as user_repo
from src.repositories.booking import BookingRepository as booking_repo


logger = logging.getLogger(__name__)


async def create_user(session: AsyncSession, user_data: SUserCreate) -> SUserResponse:
    # Используем метод, который загружает связанные данные (eager loading) и ищет по telegram_id.
    # Название метода `get_by_telegram_id_with_relations` - это пример.
    # Замените его на ваш реальный метод из репозитория.
    user = await user_repo(session).get_id(telegram_id=user_data.telegram_id) # Предполагаем, что get_id теперь загружает связи

    if user:
        total_bookings = await booking_repo(session).statistic_total(user.id)
        completed_bookings = await booking_repo(session).statistic_completed(user.id)
    else:
        user = user_data.to_orm_model()
        if not user:
            logger.error(f"Не удалось создать пользователя: {user_data}")
            raise HTTPException(detail="Не удалось создать пользователя", status_code=500)
            
        session.add(user)
        await session.flush()  # Получаем user.id из базы данных
        await session.refresh(user)
        # Для нового пользователя статистика всегда 0
        total_bookings = 0
        completed_bookings = 0
    
    # Используем from_attributes=True, что является стандартной практикой
    # для преобразования ORM моделей в Pydantic.
    response = SUserResponse.model_validate(user, from_attributes=True)
    response.total_bookings = total_bookings
    response.completed_bookings = completed_bookings

    return response


async def verify_user(session: AsyncSession, data: SPhoneVerification):
    user = await user_repo(session).get_id(telegram_id=data.telegram_id) # Используем get_id для поиска по telegram_id
    if not user:
        logger.error(f"Пользователь не найден: {data}")
        raise HTTPException(detail="Пользователь не найден", status_code=404)
    user.phone_number = data.phone_number
    user.is_verified = True
    await session.flush()
    return {
        "status": "verified",
        "phone_number": data.phone_number
    }





async def find_user(session: AsyncSession, **filter_by) -> SUserResponse:
    user = await user_repo(session).get_id(**filter_by) # Используем get_id для поиска по произвольным фильтрам
    if not user:
        logger.error(f"Пользователь не найден: {filter_by}")
        raise HTTPException(detail="Пользователь не найден", status_code=404)
    total_booking = await booking_repo(session).statistic_total(user.id)
    completed_booking = await booking_repo(session).statistic_completed(user.id)
    """user.total_bookings = total_booking
    user.completed_bookings = completed_booking"""
    return SUserResponse.model_validate(user, from_attributes=True)


async def find_all_users(
    session: AsyncSession, skip: int = 0, limit: int = 100, **filter_by
) -> List[SUserResponse]:
    users = await user_repo(session).get_all(skip, limit, **filter_by)
    if not users:
        logger.error(f"Пользователи не найдены: {filter_by}")
        raise HTTPException(detail="Пользователи не найдены", status_code=404)
    return [SUserResponse.model_validate(user, from_attributes=True) for user in users]


async def update_user(
    session: AsyncSession, data: SUserUpdate
) -> SUserResponse:

    user = await user_repo(session).get_id(id=data.telegram_id)
    if not user:
        logger.error(f"Пользователь не найден: {data.telegram_id}")
        raise HTTPException(detail="Пользователь не найден", status_code=404)

    data.apply_update(user)
    await session.flush()
    await session.refresh(user)
    return SUserResponse.model_validate(user, from_attributes=True)


async def delete_user(session: AsyncSession, user_id: uuid.UUID):
    user = await user_repo(session).get_id(id=user_id)
    if not user:
        logger.error(f"Пользователь не найден: {user_id}")
        raise HTTPException(detail="Пользователь не найден", status_code=404)
    await session.delete(user)


async def get_for_admins(session: AsyncSession, **filter_by) -> SUserResponse:
    user = await user_repo(session).get_all(**filter_by)
    if not user:
        logger.error(f"Пользователь не найден: {filter_by}")
        raise HTTPException(detail="Пользователь не найден", status_code=404)
    return SUserResponse.model_validate(user, from_attributes=True)