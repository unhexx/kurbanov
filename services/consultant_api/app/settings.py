from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://consultant:consultant@localhost:5432/consultant"

    telegram_bot_token: str = ""
    telegram_webhook_secret_token: str = ""
    telegram_manager_chat_id: str = ""

    admin_api_token: str = ""

    cbr_daily_url: str = "https://www.cbr.ru/scripts/XML_daily.asp"
    formula_version: str = "v1.0"


settings = Settings()

