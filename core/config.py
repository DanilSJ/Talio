import pathlib
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from yookassa import Configuration

load_dotenv()

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    PROXY: str = os.getenv("PROXY")

    db_url: str = f"sqlite+aiosqlite:///{BASE_DIR}/db.sqlite3"
    DB_ECHO: bool = os.getenv("DB_ECHO", "False") == "False"
    DB_POOL_NULL: bool = os.getenv("DB_POOL_NULL", "False") == "True"

    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL")

    YOOKASSA_ID: int = os.getenv("YOOKASSA_ID")
    YOOKASSA_KEY: str = os.getenv("YOOKASSA_KEY")


settings = Settings()
Configuration.configure("<Account Id>", "<Secret Key>")
