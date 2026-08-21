import asyncpg
from pgvector.asyncpg import register_vector

from fastapi import FastAPI
from loguru import logger


from app.core.settings.app import AppSettings


async def connect_to_db(app: FastAPI, settings: AppSettings) -> None:
    logger.info("Connecting to PostgreSQL")

    app.state.pool = await asyncpg.create_pool(
        str(settings.database_url),
        ssl=False,
        min_size=settings.min_connection_count,
        max_size=settings.max_connection_count,
        init=register_vector
    )

    logger.info("Connection established")


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")

    await app.state.pool.close()

    logger.info("Connection closed")
