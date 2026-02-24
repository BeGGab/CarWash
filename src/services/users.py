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
    existing_user = await user_repo(session).get_one_or_none(telegram_id=user_data.telegram_id)
    if existing_user:
        logger.warning(f"Попытка создать уже существующего пользователя: {user_data.telegram_id}")
        return await find_user(session, telegram_id=user_data.telegram_id)

    new_user_orm = user_repo.model(**user_data.model_dump())
    session.add(new_user_orm)
    await session.flush()
    await session.refresh(new_user_orm)
    logger.info(f"Создан новый пользователь: {new_user_orm.telegram_id}")

    return  SUserResponse.model_validate(new_user_orm, from_attributes=True)


async def verify_user(session: AsyncSession, data: SPhoneVerification):
    user = await user_repo(session).get_one_or_none(telegram_id=data.telegram_id) 
    if not user:
        logger.error(f"Пользователь не найден: {data}")
        raise HTTPException(detail="Пользователь не найден", status_code=404)
    user.phone_number = data.phone_number
    user.is_verified = True
    await session.flush()
    return await find_user(session, telegram_id=data.telegram_id)


async def find_user(session: AsyncSession, **filter_by) -> SUserResponse:
    user = await user_repo(session).get_one_or_none(**filter_by) 
    if not user:
        logger.error(f"Пользователь не найден: {filter_by}")
        raise HTTPException(detail="Пользователь не найден", status_code=404)
    total_booking = await booking_repo(session).statistic_total(user.id)
    completed_booking = await booking_repo(session).statistic_completed(user.id)
    
    # Собираем ответ, включая статистику
    user_data_dict = user.__dict__
    user_data_dict['total_bookings'] = total_booking
    user_data_dict['completed_bookings'] = completed_booking
    
    return SUserResponse.model_validate(user_data_dict, from_attributes=True)


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

    user = await user_repo(session).get_one_or_none(telegram_id=data.telegram_id)
    if not user:
        logger.error(f"Пользователь не найден: {data.telegram_id}")
        raise HTTPException(detail="Пользователь не найден", status_code=404)

    # data.apply_update(user) # Этот метод может быть небезопасным, лучше обновлять поля явно
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
        
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return SUserResponse.model_validate(user, from_attributes=True)


async def delete_user(session: AsyncSession, user_id: uuid.UUID):
    user = await user_repo(session).get_one_or_none(id=user_id)
    if not user:
        logger.error(f"Пользователь не найден: {user_id}")
        raise HTTPException(detail="Пользователь не найден", status_code=404)
    await session.delete(user)


async def get_for_admins(session: AsyncSession, **filter_by) -> SUserResponse:
    user = await user_repo(session).get_one_or_none(**filter_by)
    if not user:
        logger.error(f"Пользователь не найден: {filter_by}")
        raise HTTPException(detail="Пользователь не найден", status_code=404)
    return SUserResponse.model_validate(user, from_attributes=True)