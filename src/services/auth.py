from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.telegram_auth import validate_init_data, parse_init_data
from src.schemas.users import SUserCreate, SUserResponse, STelegramAuth
from src.services.users import UserService

from src.core.config import Settings


async def get_or_create_user_by_init_data(
    init_data: str, session: AsyncSession
) -> SUserResponse:

    if not validate_init_data(init_data, Settings().bot_token):
        raise HTTPException(status_code=401, detail="Invalid Telegram Init Data")

    parsed_data = parse_init_data(init_data)
    telegram_user_data = parsed_data.get("user")

    if not telegram_user_data or not telegram_user_data.get("id"):
        raise HTTPException(
            status_code=400, detail="Telegram user ID not found in init data"
        )

    telegram_id = telegram_user_data["id"]
    raw_username = telegram_user_data.get("username")
    username = raw_username if raw_username else f"user_{telegram_id}"

    last_name = telegram_user_data.get("last_name")

    user_create_data = SUserCreate(
        telegram_id=telegram_id,
        username=username,
        first_name=telegram_user_data.get("first_name") or "",
        last_name=last_name if last_name else None,
        email=None,
        phone_number=None,
        is_verified=False,
    )

    user_service = UserService(session)
    user = await user_service.create_user(user_create_data)
    return user
