import os
from typing import List

from pydantic import PostgresDsn, Field, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Основные настройки
    postgres_url: PostgresDsn = Field(env="postgres_url")
    bot_token: str
    admins_id: List[int]

    # Ссылка для Mini app
    webapp_url: str

    # Адрес API
    api_base_url: str = "http://localhost:8000"

    # Настройки Redis
    redis_url: RedisDsn

    # Настройки платежной системы
    yookassa_shop_id: str
    yookassa_secret_key: str

    class Config:
        env_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
        )
        env_file_encoding = "utf-8"
        case_sensitive = False
