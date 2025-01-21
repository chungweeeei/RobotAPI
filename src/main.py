import uvicorn
import structlog

from fastapi import FastAPI

from settings.settings import postgres_settings
from database.postgres import connect_to_postgres

from api.settings.settings import init_settings_router

if __name__ == "__main__":

    pg_engine = connect_to_postgres(
        host=postgres_settings.host,
        port=postgres_settings.port,
        db_name=postgres_settings.db_name,
        user=postgres_settings.user,
        password=postgres_settings.password
    )

    logger = structlog.get_logger()

    # register fastapi server
    description = """
    RobotAPI helps you do robot stuff.

    ## Configs

    ## Status

    """

    fastapi = FastAPI(title="RobotAPI",
                      description=description,
                      version="1.0.0")

    fastapi.include_router(init_settings_router())

    try:
        uvicorn.run(fastapi, host="0.0.0.0", port=3000)
    except Exception as err:
        logger.error("[RUN] Uvicorn fun fastapi server failed: {}".format(err))
        exit()
