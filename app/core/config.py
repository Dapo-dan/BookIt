from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    app_env: str = os.getenv("APP_ENV", "dev")
    debug: bool = os.getenv("APP_DEBUG", "true").lower() == "true"
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me")
    jwt_alg: str = os.getenv("JWT_ALG", "HS256")
    access_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    refresh_minutes: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 43200))
    bcrypt_rounds: int = int(os.getenv("BCRYPT_ROUNDS", 12))

    db_url_async: str = os.getenv("DATABASE_URL")
    db_url_sync: str = os.getenv("SYNC_DATABASE_URL")

settings = Settings()

