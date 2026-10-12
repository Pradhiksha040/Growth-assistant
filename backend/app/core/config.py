"""
Configuration module for The Lenny Growth Assistant.
Uses Pydantic Settings for environment-driven configuration with sensible defaults.
"""
from typing import List, Optional
import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "The Lenny Growth Assistant"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    API_V1_PREFIX: str = "/api/v1"
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/lenny_growth",
        description="PostgreSQL connection string. Falls back to SQLite if unreachable."
    )
    SQLITE_FALLBACK_URL: str = "sqlite:///./data/lenny_assistant.db"
    DB_POOL_PRE_PING: bool = True
    DB_ECHO: bool = False
    
    # Active Provider Setting: 'ollama' | 'anthropic' | 'openai' | 'offline'
    DEFAULT_PROVIDER: str = Field(default="ollama", description="Default LLM provider")
    
    # Local Provider: Ollama
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434",
        description="Base URL for local Ollama server"
    )
    OLLAMA_MODEL: str = Field(
        default="llama3.2",
        description="Model name to pull/use on Ollama"
    )
    OLLAMA_TIMEOUT_SECONDS: float = 60.0
    
    # Cloud Provider: Anthropic Claude
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic API Key")
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    
    # Cloud Provider: OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API Key")
    OPENAI_MODEL: str = "gpt-4o"
    
    # Knowledge Base & Retrieval
    DATA_DIR: str = "data"
    TRANSCRIPTS_DIR: str = "data/transcripts"
    CHUNK_SIZE: int = 650
    CHUNK_OVERLAP: int = 120
    TOP_K_RETRIEVAL: int = 5
    SIMILARITY_THRESHOLD: float = 0.15
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

settings = Settings()
