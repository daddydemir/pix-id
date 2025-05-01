from pydantic import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:pass@postgre:5432/db_name"
    )
    IMAGE_FOLDER : str = os.getenv(
        "IMAGE_FOLDER", 
        "app/static/uploads"
    )
    FACE_FOLDER : str = os.getenv(
        "FACE_FOLDER", 
        "app/static/detected_faces"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()