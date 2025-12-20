
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class BaseConfig:
    ENV = os.getenv("FLASK_ENV", os.getenv("ENV", "development")).lower()
    DEBUG = ENV != "production"

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(5 * 1024 * 1024)))

    MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "trained_model.h5"))

    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "false").lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
    }
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "60 per minute")

    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


def get_config_class() -> type[BaseConfig]:
    env = os.getenv("FLASK_ENV", os.getenv("ENV", "development")).lower()
    if env == "production":
        return ProductionConfig
    return DevelopmentConfig

