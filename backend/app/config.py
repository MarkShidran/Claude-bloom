from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://bloom:bloom_dev@db:5432/bloom"
    DATABASE_ECHO: bool = False

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # MOEX ISS API
    MOEX_BASE_URL: str = "https://iss.moex.com/iss"

    # CBR
    CBR_BASE_URL: str = "https://www.cbr.ru/scripts"

    # E-Disclosure
    EDISCLOSURE_BASE_URL: str = "https://e-disclosure.ru"

    # Scheduler cron expressions
    QUOTE_SYNC_CRON: str = "0 19 * * 1-5"
    FX_SYNC_CRON: str = "0 15 * * *"
    MACRO_SYNC_CRON: str = "0 10 1 * *"

    # Excel upload
    MAX_UPLOAD_SIZE_MB: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
