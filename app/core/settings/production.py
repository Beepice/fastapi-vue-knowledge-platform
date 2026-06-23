from app.core.settings.app import AppSettings
import logging
from typing import List


class ProdAppSettings(AppSettings):
    title: str = "Dev FastAPI example application"
    logging_level: int = logging.WARNING
    allowed_hosts: List[str] = ["*"]
    debug: bool = False
    istraceback: bool = False

    class Config(AppSettings.Config):
        env_file = ".env"
