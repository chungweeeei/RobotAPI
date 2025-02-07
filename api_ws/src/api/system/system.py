import structlog

from fastapi import (
    APIRouter,
    status
)

from repository.version.version import VersionRepo

def init_system_router(version_repo: VersionRepo) -> APIRouter:

    system_router = APIRouter(prefix="", tags=["System"])

    @system_router.post("/v1/system/restart")
    def restart_system():
        return status.HTTP_200_OK

    @system_router.get("/v1/system/status")
    def get_system_status():
        return status.HTTP_200_OK

    return system_router