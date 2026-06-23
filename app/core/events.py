from typing import Callable

from fastapi import FastAPI
from loguru import logger

from app.core.settings.app import AppSettings
from app.db.events import close_db_connection, connect_to_db


async def create_start_app_handler(
    app: FastAPI,
    settings: AppSettings,
) -> None:  # type: ignore
    await connect_to_db(app, settings)


async def create_stop_app_handler(app: FastAPI) -> None:  # type: ignore
    with logger.catch(message="close_db_connection fail"):
        await close_db_connection(app)
