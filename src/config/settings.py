import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str
    tavily_api_key: str

    # Database
    vector_db_path: str = "./data/vector_db"
    upload_path: str = "./data/uploads"

    # Model Configuration
    llm_model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-ada-002"
    temperature: float = 0.7
    max_tokens: int = 1000

    # Search Configuration
    max_search_results: int = 5
    search_timeout: int = 10

    # Memory Configuration
    memory_window: int = 10
    max_memory_tokens: int = 4000

    class Config:
        env_file = ".env"

settings = Settings()