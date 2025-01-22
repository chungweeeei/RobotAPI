from fastapi import (
    APIRouter,
    status
)

from api.settings.schemas import SettingsResp


from fastapi.responses import JSONResponse


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

    @settings_router.get("/v1/settings/category",
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
    def get_settings():
        return status.HTTP_404_NOT_FOUND

    return settings_router