"""
Configuration module for Rag Innovations backend.
Loads environment variables and provides a single settings object.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # API Keys
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Vector Database
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "RagInno_DB")

    # LLM Configuration (accessible on Groq)
    LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")

    # CORS — comma-separated origins
    CORS_ORIGINS: list = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3000"
        ).split(",")
        if origin.strip()
    ]

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()
