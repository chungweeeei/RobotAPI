import uvicorn
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings.settings import postgres_settings
from database.postgres import connect_to_postgres

from communication.tcp_server import setup_tcp_server

from repository.file.file import setup_file_repo
from repository.map.map import setup_map_repo
from repository.robot.robot import setup_robot_repo
from repository.user.user import setup_user_repo
from repository.version.version import setup_version_repo
from repository.setting.setting import setup_setting_repo

from api.settings.settings import init_settings_router
from api.file.file import init_file_router
from api.map.map import init_map_router
from api.user.login import init_login_router
from api.user.user import init_user_router
from api.version.version import init_version_router
from api.system.system import init_system_router

from middleware import observability
from logger import context_logger

if __name__ == "__main__":

    pg_engine = connect_to_postgres(
        host=postgres_settings.host,
        port=postgres_settings.port,
        db_name=postgres_settings.db_name,
        user=postgres_settings.user,
        password=postgres_settings.password
    )

    # register fastapi server
    description = """
    RobotAPI helps you do robot stuff.

    ## Configs

    ## Status

    """

    fastapi = FastAPI(title="RobotAPI",
                      description=description,
                      version="1.0.0")
    
    """
        {TODO} What is CORS?
    """
    fastapi.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # regsiter http middleware
    observability.register(app=fastapi)

    # setup each repo
    file_repo = setup_file_repo(logger=context_logger)
    map_repo = setup_map_repo(logger=context_logger, engine=pg_engine)
    robot_repo = setup_robot_repo(logger=context_logger, engine=pg_engine)
    user_repo = setup_user_repo(logger=context_logger, engine=pg_engine)
    version_repo = setup_version_repo(logger=context_logger, engine=pg_engine)
    setting_repo = setup_setting_repo(logger=context_logger)

    # setup each router
    fastapi.include_router(init_settings_router(setting_repo=setting_repo))
    fastapi.include_router(init_map_router(map_repo=map_repo))
    fastapi.include_router(init_file_router(file_repo=file_repo))
    fastapi.include_router(init_login_router(user_repo=user_repo))
    fastapi.include_router(init_user_router(user_repo=user_repo))
    fastapi.include_router(init_version_router(version_repo=version_repo))
    fastapi.include_router(init_system_router(version_repo=version_repo))
    
    # # setup communication
    # tcp_server = setup_tcp_server(logger=context_logger, 
    #                               robot_repo=robot_repo)
    
    # tcp_server_thread = threading.Thread(target=tcp_server.listen)
    # tcp_server_thread.start()

    try:
        context_logger.info("Running API Server")
        uvicorn.run(fastapi, host="0.0.0.0", port=3000)
    except Exception as err:
        context_logger.error("[RUN] Uvicorn fun fastapi server failed: {}".format(err))
        exit()
