from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()
load_dotenv("app/.env")


@dataclass(frozen=True)
class Settings:
    database_url: str | None = os.getenv("DATABASE_STRING") or os.getenv("DATABASE_URL")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key")


settings = Settings()
