import uuid
import logging 
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession


from src.schemas.users import SUserCreate, SUserUpdate, SUserResponse

from src.repositories.users import UserRepository as user_repo



logger = logging.getLogger(__name__)



async def create_user(session: AsyncSession, user_data: SUserCreate) -> SUserResponse:
    user = user_data.to_orm_model()
    if not user:
        logger.error(f"Ошибка при создании пользователя: {user_data}")
        # raise to be

    session.add(user)
    await session.flush()
    await session.refresh(user)
    return SUserResponse.model_validate(user, from_attributes=True)


async def find_user(session: AsyncSession, **filter_by) -> SUserResponse:
    user = await user_repo(session).get_id(**filter_by)
    if not user:
        logger.error(f"Пользователь не найден: {filter_by}")
        # raise to be
    return SUserResponse.model_validate(user, from_attributes=True)



async def find_all_users(session: AsyncSession, skip: int = 0, limit: int = 100, **filter_by) -> List[SUserResponse]:
    users = await user_repo(session).get_all(skip, limit, **filter_by)
    if not users:
        logger.error(f"Пользователи не найдены: {filter_by}")
        # raise to be
    return [SUserResponse.model_validate(user, from_attributes=True) for user in users]



async def update_user(session: AsyncSession, user_id: uuid.UUID, data: SUserUpdate) -> SUserResponse:
    user = await user_repo(session).get_id(id=user_id)
    if not user:
        logger.error(f"Пользователь не найден: {user_id}")
        # raise to be

    data.apply_update(user)
    await session.flush()
    await session.refresh(user)
    return SUserResponse.model_validate(user, from_attributes=True)


async def delete_user(session: AsyncSession, user_id: uuid.UUID):
    user = await user_repo(session).get_id(id=user_id)
    if not user:
        logger.error(f"Пользователь не найден: {user_id}")
        # raise to be
    await session.delete(user)