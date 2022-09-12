from pydantic import BaseSettings


class Settings(BaseSettings):
    telegram_token: str = "your-telegram-token"


settings = Settings()