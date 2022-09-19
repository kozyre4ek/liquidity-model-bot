from pydantic import BaseSettings


class Settings(BaseSettings):
    telegram_token: str = "your-telegram-token"
    telegram_admin_id: int


settings = Settings()