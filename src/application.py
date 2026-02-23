import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse # Это не используется для default_response_class

from src.routers.v1.carwash import router as carwash_router
from src.routers.v1.booking import router as booking_router
from src.routers.v1.payment import router as payment_router
from src.routers.v1.user import router as user_router
from src.routers.v1.washtype import router as washtype_router
from src.bot.main import main as run_bot

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    bot_task = asyncio.create_task(run_bot())
    yield
    bot_task.cancel()


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="CarWash API",
        description="API для агрегатора автомоек с бронированием и предоплатой",
        version="1.0.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=JSONResponse,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        # Добавляем явные адреса для локальной разработки и ngrok
        allow_origins=[
            "http://localhost:3000",  # Стандартный порт React
            "http://localhost:5173",  # Стандартный порт Vite
            # ВАЖНО: Добавьте сюда ваш ngrok URL для тестов в Telegram
            "https://c7c1-144-31-207-241.ngrok-free.app" # <-- ВАША NGROK ССЫЛКА
        ],
        allow_credentials=True,
        # Регулярное выражение для поддержки всех поддоменов Telegram
        allow_origin_regex=r"https://.*\.telegram\.org",
        allow_methods=["*"],
        allow_headers=["*"],
    )

    
    logger.info("Запуск CarWash API")
    
    app.include_router(carwash_router)
    app.include_router(booking_router)
    app.include_router(payment_router)
    app.include_router(user_router)
    app.include_router(washtype_router)
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "carwash-api"}

    return app