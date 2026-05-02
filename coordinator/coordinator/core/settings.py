from pydantic_settings import BaseSettings


# Reads from environment variables
class Settings(BaseSettings):
    user_service_url: str
    book_service_url: str


settings = Settings()
