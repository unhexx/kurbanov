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

    # Внешний сервис формирования ответов консультанта.
    # Реальные значения берутся из .env, в репозиторий не коммитятся.
    perplexity_api_key: str = ""
    perplexity_base_url: str = "https://api.perplexity.ai"
    perplexity_model: str = "sonar-pro"
    perplexity_max_tokens: int = 800
    perplexity_temperature: float = 0.2
    perplexity_timeout_seconds: float = 30.0
    perplexity_max_retries: int = 2
    # Минимальный бюджет, ниже которого подбор переадресуется менеджеру (RUB).
    budget_threshold_rub: int = 1_500_000
    # Сколько последних сообщений диалога передавать в модель.
    consultant_history_limit: int = 12


settings = Settings()
