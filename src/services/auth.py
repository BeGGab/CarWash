from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.telegram_auth import validate_init_data, parse_init_data
from src.schemas.users import SUserCreate, SUserResponse
from src.services.users import create_user


async def get_or_create_user_by_init_data(
    init_data: str, session: AsyncSession
) -> SUserResponse:
    """
    Сервисная функция для аутентификации пользователя по Telegram Init Data.
    1. Валидирует и парсит init_data.
    2. Извлекает данные пользователя.
    3. Вызывает сервис для поиска или создания пользователя в БД.
    """
    if not validate_init_data(init_data):
        raise HTTPException(status_code=401, detail="Invalid Telegram Init Data")

    parsed_data = parse_init_data(init_data)
    telegram_user_data = parsed_data.get("user")

    if not telegram_user_data or not telegram_user_data.get("id"):
        raise HTTPException(status_code=400, detail="Telegram user ID not found in init data")

    user_create_data = SUserCreate.model_validate(telegram_user_data)

    # Сервис create_user уже содержит логику поиска или создания пользователя
    user = await create_user(session, user_create_data)
    return user