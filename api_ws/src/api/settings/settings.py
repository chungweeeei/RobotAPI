import structlog

from fastapi import (
    APIRouter,
    status,
    Depends
)

from api.settings.schemas import (
    SystemSettingsResp,
    MoveSettingsResp,
    SettingsResp,
)

from dependecy.dependencies import (
    extract_bind_logger,
    allow_all_user
)

def init_settings_router() -> APIRouter:

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
                         response_model=SettingsResp,
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

        resp = SettingsResp(system=SystemSettingsResp(robot_id="robot2",
                                                      robot_name="robot2",
                                                      map="test1",
                                                      initial_pose_x=5.0,
                                                      initial_pose_y=5.0,
                                                      initial_pose_yaw=0.0),
                            move=MoveSettingsResp(max_linear_speed=1.0,
                                                  max_angular_speed=0.3))

        return resp
    
    @settings_router.put("/v1/settings/system",
                         dependencies=[Depends(allow_all_user)])
    def set_system_settings():
        return status.HTTP_200_OK
    
    return settings_router