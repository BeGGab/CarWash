import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session

from src.schemas.users import (
    SUserUpdate,
    SUserResponse,
    SPhoneVerification,
)
from src.services.users import (
    verify_user,
    find_user,
    find_all_users,
    update_user,
    delete_user,
    get_for_admins,
)

from src.services.auth import get_or_create_user_by_init_data


router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.post(
    "/telegram/auth",
    summary="Аутентификация пользователя Mini App",
    status_code=status.HTTP_200_OK,
)
async def telegram_auth(
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    session: AsyncSession = Depends(get_async_session),
) -> SUserResponse:
    """
    Эндпоинт для аутентификации пользователя Mini App через Telegram Init Data.
    Если пользователь существует, возвращает его данные. Если нет - создает нового.
    """
    user = await get_or_create_user_by_init_data(init_data, session)
    return user


@router.post("/verify-phone")
async def verify_phone(
    data: SPhoneVerification, session: AsyncSession = Depends(get_async_session)
):
    """
    Верификация номера телефона

    Telegram Mini App отправляет номер телефона через requestContact
    """
    return verify_user(session, data)


@router.get("/me")
async def get_current_user(
    x_telegram_id: int = Header(..., description="Telegram ID пользователя"),
    session: AsyncSession = Depends(get_async_session),
) -> SUserResponse:
    return await find_user(session, telegram_id=x_telegram_id)


@router.patch("/me")
async def update_current_user(
    data: SUserUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> SUserResponse:
    return await update_user(session, data)


@router.get("/{user_id}")
async def get_user(
    user_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
) -> SUserResponse:
    return get_for_admins(session, id=user_id)


@router.get("/")
async def get_all_users(
    session: AsyncSession = Depends(get_async_session),
) -> list[SUserResponse]:
    return find_all_users(session)


@router.delete("/{user_id}")
async def delete(id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    await delete_user(session, id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
