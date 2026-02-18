import logging
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config_logging import setup_logging
from src.exception.exception_handlers import setup_exception_handlers
from src.routers.v1.user import router as user_router
from src.routers.v1.author import router as author_router
from src.routers.v1.student import router as student_router
from src.routers.v1.courses import router as courses_router


setup_logging()

logger = logging.getLogger(__name__)


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=JSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[],  # Указывайте здесь домены вашего фронтенда
        allow_credentials=True,
        allow_origin_regex=r"http://localhost:.*",  # Для локальной разработки
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("Запуск приложения")
    app.include_router(user_router)
    app.include_router(author_router)
    app.include_router(student_router)
    app.include_router(courses_router)
    setup_exception_handlers(app)

    return app