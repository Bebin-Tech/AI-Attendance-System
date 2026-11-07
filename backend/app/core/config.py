from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AIFAMS_", env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = (
        "postgresql+asyncpg://aifams_runtime:aifams_runtime_local@localhost:5432/aifams"
    )
    migration_database_url: str = "postgresql+asyncpg://aifams:aifams_local@localhost:5432/aifams"
    redis_url: str = "redis://localhost:6379/0"
