"""
Главный файл Telegram бота CarWash
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.core.config import Settings
from src.bot.handlers import user_router, booking_router, admin_wash_router
from src.bot.admin_panel.admin import admin_router as system_admin_router 
from src.bot.handlers.user import setup_config as setup_user_config
from src.bot.handlers.booking import setup_config as setup_booking_config
from src.bot.handlers.admin_wash import setup_config as setup_admin_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Запуск бота"""
    settings = Settings()
    
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    admin_ids = [settings.admins_id]
    webapp_url = settings.webapp_url
    
    setup_user_config(admin_ids, webapp_url)
    setup_booking_config(admin_ids, webapp_url)
    setup_admin_config(admin_ids)
    
    dp.include_router(user_router)
    dp.include_router(booking_router)
    dp.include_router(admin_wash_router)
    dp.include_router(system_admin_router) # Подключаем роутер
    
    logger.info("Запуск CarWash бота...")
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
