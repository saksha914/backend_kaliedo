from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database Configuration
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name: str = os.getenv("DATABASE_NAME", "kaliedo_synergy")
    
    # JWT Configuration
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-here-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Application Configuration
    app_name: str = os.getenv("APP_NAME", "Kaleido Synergy Assessment Centre")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings() 