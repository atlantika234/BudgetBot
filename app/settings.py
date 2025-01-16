from dotenv import load_dotenv
from pydantic import BaseModel
import os

load_dotenv(override=True)

class Settings(BaseModel):
    TELEGRAM_BOT_TOKEN: str = os.getenv("BOT_TOKEN")

config = Settings()
