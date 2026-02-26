import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.routers.v1.carwash import router as carwash_router
from src.routers.v1.booking import router as booking_router
from src.routers.v1.payment import router as payment_router
from src.routers.v1.user import router as user_router
from src.routers.v1.washtype import router as washtype_router
from src.bot.main import main as run_bot
from src.core.config import Settings

settings = Settings()

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
        # Добавляем явные адреса для локальной разработки, ngrok и webapp
        allow_origins=[
            "http://localhost:3000",  # Стандартный порт React
            "http://localhost:5173",  # Стандартный порт Vite
            # Публичный URL Mini App и API (например, туннель)
            settings.webapp_url,
            settings.api_base_url,
        ],
        # allow_origins=["*"] # Для отладки можно временно разрешить все источники
        allow_credentials=True,
        # Регулярное выражение для поддержки всех поддоменов Telegram
        allow_origin_regex=r"https://.*\.telegram\.org",
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключаем статику и шаблоны для Mini App (React-сборка через Jinja2)
    templates = Jinja2Templates(directory="webapp/dist")
    # Vite по умолчанию кладёт assets в webapp/dist/assets
    app.mount("/assets", StaticFiles(directory="webapp/dist/assets"), name="assets")

    logger.info("Запуск CarWash API")

    app.include_router(carwash_router)
    app.include_router(booking_router)
    app.include_router(payment_router)
    app.include_router(user_router)
    app.include_router(washtype_router)

    @app.get("/miniapp")
    async def miniapp(request: Request):
        """
        Точка входа Mini App.
        Отдаёт собранный index.html через Jinja2, а статику раздаёт FastAPI.
        """
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "carwash-api"}

    return app
