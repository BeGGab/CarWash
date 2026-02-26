from src.bot.handlers.user import router as user_router
from src.bot.handlers.booking import router as booking_router
from src.bot.handlers.system_admin import router as system_admin_router
from src.bot.handlers.carwash_admin import router as carwash_admin_router

__all__ = [
    "user_router",
    "booking_router",
    "system_admin_router",
    "carwash_admin_router",
]
