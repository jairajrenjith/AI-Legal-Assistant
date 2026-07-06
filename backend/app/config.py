import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./legal_assistant.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))


settings = Settings()
