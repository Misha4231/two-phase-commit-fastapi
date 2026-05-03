from pydantic_settings import BaseSettings


# Reads from environment variables
class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    postgres_db: str

    redis_host: str
    redis_password: str
    redis_port: str


settings = Settings()
