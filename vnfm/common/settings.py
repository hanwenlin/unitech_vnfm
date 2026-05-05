from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "L-VNFM"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://vnfm:vnfm@localhost:5433/vnfm"
    sync_database_url: str = "postgresql://vnfm:vnfm@localhost:5432/vnfm"
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    redis_url: str = "redis://localhost:6379/0"
    default_page_size: int = 20
    bootstrap_admin_username: str = "admin"
    bootstrap_admin_password: str = "admin"
    bootstrap_admin_tenant: str = "default"

    @field_validator("secret_key")
    @classmethod
    def _validate_secret_key(cls, v: str) -> str:
        if not v:
            raise ValueError(
                "VNFM_SECRET_KEY is required; generate with "
                "`python -c \"import secrets; print(secrets.token_urlsafe(48))\"`"
            )
        if "change-in-production" in v.lower():
            raise ValueError(
                "VNFM_SECRET_KEY is set to the placeholder value; choose a strong random secret"
            )
        if len(v) < 32:
            raise ValueError("VNFM_SECRET_KEY must be at least 32 characters long")
        return v

    class Config:
        env_prefix = "VNFM_"
        env_file = ".env"


settings = Settings()