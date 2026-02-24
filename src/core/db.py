from contextlib import asynccontextmanager
import sqlalchemy as sa
from typing import Optional
from typing import Annotated, List, AsyncGenerator
from sqlalchemy import Text, String, ARRAY
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeMeta, declarative_base, class_mapper, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


from src.core.config import Settings


settings = Settings()
engine = create_async_engine(str(settings.postgres_url))
async_session_maker = async_sessionmaker(engine,class_=AsyncSession, expire_on_commit=True, autoflush=False, autocommit=False)


uniq_str_an = Annotated[str, mapped_column(Text, unique=True, nullable=False)]
array_or_none_an = Annotated[List[str] | None, mapped_column(ARRAY(String))]


metadata = sa.MetaData()

class BaseServiceModel(AsyncAttrs):
    __abstract__ = True


    """Базовый класс для таблиц сервиса."""

    @classmethod
    def on_conflict_constrauuid(cls) -> Optional[tuple]:
        return None
    
    def to_dict(self) -> dict:
        """Универсальный метод для конвертации объекта SQLAlchemy в словарь"""
        # Получаем маппер для текущей модели
        columns = class_mapper(self.__class__).columns
        # Возвращаем словарь всех колонок и их значений
        return {column.key: getattr(self, column.key) for column in columns}


Base: DeclarativeMeta = declarative_base(metadata=metadata, cls=BaseServiceModel)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()