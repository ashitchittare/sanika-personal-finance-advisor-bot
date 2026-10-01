import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project (Personal-Finance-Advisor-Bot root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
load_dotenv(BASE_DIR / ".env")

# Instance directory path
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_SQLITE_PATH = (INSTANCE_DIR / "finance.db").resolve().as_posix()


class Config:
    """Base Configuration"""
    SECRET_KEY = os.getenv("SECRET_KEY", "finance-advisor-bot-super-secret-key-2026")
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        # If user passed a relative sqlite path or generic URI
        if DATABASE_URL.startswith("sqlite:///instance/"):
            db_filename = DATABASE_URL.replace("sqlite:///instance/", "")
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{(INSTANCE_DIR / db_filename).resolve().as_posix()}"
        elif DATABASE_URL.startswith("sqlite:///") and not os.path.isabs(DATABASE_URL.replace("sqlite:///", "")):
            rel_path = DATABASE_URL.replace("sqlite:///", "")
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{(BASE_DIR / rel_path).resolve().as_posix()}"
        else:
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DEFAULT_SQLITE_PATH}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AI Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # App settings
    CURRENCY_SYMBOL = "₹"
    CURRENCY_CODE = "INR"
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True


class TestingConfig(Config):
    """Testing Configuration"""
    TESTING = True
    DEBUG = True
    # In-memory or isolated test database
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    # Use environment secret key in production
    SECRET_KEY = os.getenv("SECRET_KEY", "prod-must-set-random-secret-key-348927498234")


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
