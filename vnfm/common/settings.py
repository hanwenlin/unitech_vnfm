from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "L-VNFM"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://vnfm:vnfm@localhost:5432/vnfm"
    sync_database_url: str = "postgresql://vnfm:vnfm@localhost:5432/vnfm"
    secret_key: str = "super-secret-jwt-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    redis_url: str = "redis://localhost:6379/0"
    default_page_size: int = 20

    class Config:
        env_prefix = "VNFM_"
        env_file = ".env"


settings = Settings()