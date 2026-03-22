from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    api_key: str
    database_url: str = "sqlite:///./data/conversations.db"
    
    class Config:
        env_file = ".env"
        env_prefix = "DATA_COLLECTION_"


@lru_cache
def get_settings() -> Settings:
    return Settings()
