from fastapi import (
    APIRouter,
    status
)

from api.settings.schemas import SettingsResp


from fastapi.responses import JSONResponse
from pydantic import BaseModel


class Message(BaseModel):
    message: str

def init_settings_router() -> APIRouter:

    settings_router = APIRouter(prefix="", tags=["Settings"])

    """
        additional response with model

        you can pass to your pass operation decorators a parameter models

        it receives a dict: the key are status codes, and the value are other dicts
        with the information for each of them.
    """

    """
        response_model is used to define the endpoint
    """

    @settings_router.get("/v1/settings/category",
                         response_model=SettingsResp,
                         responses={status.HTTP_404_NOT_FOUND: {"model": Message}})
    def get_settings():
        return JSONResponse(status_code=404, content={"message": "Settings not found"})

    return settings_router