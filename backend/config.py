"""
Configuration management using Pydantic Settings.
All configuration is read from environment variables.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str
    
    # OpenAI
    openai_api_key: str
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-3.5-turbo"
    embedding_dimension: int = 1536
    
    # API Configuration
    frontend_url: str = "http://localhost:5173"
    
    # RAG Configuration
    retrieval_k: int = 3
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
