import logging
from typing import List

from app.core.settings.app import AppSettings


class DevAppSettings(AppSettings):
    debug: bool = True

    title: str = "Dev FastAPI example application"

    logging_level: int = logging.DEBUG

    allowed_hosts: List[str] = ["*"]

    class Config(AppSettings.Config):
        env_file = ".env"
