import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "LifeLink API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "lifelink-hackathon-super-secret-key-2026-critical-care")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./lifelink.db")

settings = Settings()
