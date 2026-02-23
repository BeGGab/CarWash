from src.bot.handlers.user import router as user_router
from src.bot.handlers.booking import router as booking_router
from src.bot.handlers.admin_wash import router as admin_wash_router

__all__ = ["user_router", "booking_router", "admin_wash_router"]
