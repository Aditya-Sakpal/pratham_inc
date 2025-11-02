"""
Configuration settings for the application
Loads environment variables and provides configuration
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pathlib import Path


# Get project root directory (two levels up from this file)
_project_root = Path(__file__).parent.parent.parent
_env_file = _project_root / '.env'


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys (required but can be set from environment)
    OPENAI_API_KEY: str = ""
    PINECONE_API_KEY: str = ""
    
    # Pinecone Configuration
    PINECONE_INDEX_NAME: str = "prathaminc"
    PINECONE_NAMESPACE: str = "ncert-science"
    PINECONE_REGION: str = "us-east-1"
    
    # OpenAI Configuration
    OPENAI_MODEL: str = "gpt-4o-mini"  # or "gpt-4" for better quality
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSIONS: int = 512
    
    # OCR Configuration
    OCR_PROVIDER: str = "openai"  # Options: openai, tesseract, easyocr, paddleocr
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # File Upload Configuration
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # Retry Configuration
    MAX_RETRIES: int = 3
    
    class Config:
        # Check if .env exists in project root
        env_file = str(_env_file) if _env_file.exists() else None
        env_file_encoding = 'utf-8'
        case_sensitive = True
        # Also check environment variables directly
        extra = 'ignore'


# Global settings instance
# Pydantic Settings will automatically load from:
# 1. Environment variables
# 2. .env file (if Config.env_file is set)
settings = Settings()

# Validate required keys and provide helpful error messages
if not settings.OPENAI_API_KEY:
    import warnings
    warnings.warn(
        "OPENAI_API_KEY not found in environment variables or .env file. "
        "Please set it in your .env file at the project root or as an environment variable.",
        UserWarning
    )

if not settings.PINECONE_API_KEY:
    import warnings
    warnings.warn(
        "PINECONE_API_KEY not found in environment variables or .env file. "
        "Please set it in your .env file at the project root or as an environment variable.",
        UserWarning
    )

