from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.utils.api_client import ApiClient


class ApiClientMiddleware(BaseMiddleware):
    """
    Middleware для передачи экземпляра ApiClient в обработчики.
    """

    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["api_client"] = ApiClient(base_url=self.base_url)
        return await handler(event, data)
