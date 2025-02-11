import structlog

from fastapi import (
    APIRouter,
    status,
    Depends,
    HTTPException
)
from fastapi.responses import JSONResponse

from api.settings import schemas as settings_schemas

from dependecy.dependencies import extract_bind_logger

from repository.setting.setting import SettingRepo
from repository.setting.schemas import (
    SystemSettings,
    MoveSettings
)
from repository.exceptions import RepoInternalError

def init_settings_router(setting_repo: SettingRepo) -> APIRouter:

    settings_router = APIRouter(prefix="", tags=["Settings"])

    """
        additional response with model

        you can pass to your pass operation decorators a parameter models

        it receives a dict: the key are status codes, and the value are other dicts
        with the information for each of them.
    """

    """
        'responses' is used to define your own return HTTP status code an detail message
        - assigned other HTTP status code
        - define your own response detail message
        - automatically generate in swagger UI

        'response_model' is used to define your return successful response model.
        - data validation
        - data filter
        - automatically generate in swagger UI
    """

    @settings_router.get("/v1/settings",
                         response_model=settings_schemas.SettingsResp,
                         responses={
                             status.HTTP_404_NOT_FOUND: {
                                 "description": "category not found",
                                 "content": {
                                     "application/json": {
                                         "message": {"detail": "testing customize response message"}
                                     }
                                 }
                             }
                         })
    def get_settings(logger=Depends(extract_bind_logger)):

        system_settings = setting_repo.get_system_settings()
        move_settings = setting_repo.get_move_settings()

        resp = settings_schemas.SettingsResp(system=settings_schemas.SystemSettings(robot_name=system_settings.robot_name,
                                                                                    map=system_settings.map,
                                                                                    initial_pose_x=system_settings.initial_pose_x,
                                                                                    initial_pose_y=system_settings.initial_pose_y,
                                                                                    initial_pose_yaw=system_settings.initial_pose_yaw),
                                             move=settings_schemas.MoveSettings(max_linear_speed=move_settings.max_linear_speed,
                                                                                max_angular_speed=move_settings.max_angular_speed))

        return resp
    
    @settings_router.put("/v1/settings/system")
    def set_system_settings(request: settings_schemas.SystemSettings):

        try:
            setting_repo.set_system_settings(settings=SystemSettings(robot_name=request.robot_name,
                                                                     map=request.map,
                                                                     initial_pose_x=request.initial_pose_x,
                                                                     initial_pose_y=request.initial_pose_y,
                                                                     initial_pose_yaw=request.initial_pose_yaw))
        except RepoInternalError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to set system settings")

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "Successfully set system settings"})
    

    @settings_router.put("/v1/settings/move")
    def set_move_settings(request: settings_schemas.MoveSettings):

        try:
            setting_repo.set_move_settings(settings=MoveSettings(max_linear_speed=request.max_linear_speed,
                                                                 max_angular_speed=request.max_angular_speed))
        except RepoInternalError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to set move settings")

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "Successfully set move settings"})
    
    return settings_router