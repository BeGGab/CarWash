import uvicorn
import asyncio
import logging

logger = logging.getLogger(__name__)


async def main() -> None:
    uvicorn.run("application:get_app", host="localhost", port=8000, factory=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Приложение остановлено")
