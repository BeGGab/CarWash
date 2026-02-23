import uvicorn
import logging

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        # Теперь uvicorn запускает и FastAPI, и бота через lifespan
        uvicorn.run("src.application:get_app", host="localhost", port=8000, factory=True, reload=True)
    except KeyboardInterrupt:
        logger.info("Приложение остановлено")
