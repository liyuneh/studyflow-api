from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-5-5"

    TELEGRAM_TOKEN: str = ""
    TELEGRAM_HANDLE: str = ""

    GMAIL_ADDRESS: str = ""
    GMAIL_APP_PASSWORD: str = ""

    TIMEZONE: str = "Africa/Nairobi"
    MORNING_PLAN_TIME: str = "07:00"
    EVENING_REVIEW_TIME: str = "21:30"

    REMINDER_MINUTES_BEFORE: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
