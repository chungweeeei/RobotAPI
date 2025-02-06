from typing import List

from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Query
)

from repository.version.version import VersionRepo
from repository.version.schemas import VersionInfo
from repository.exceptions import RepoInternalError

from api.version import schemas as version_schemas

def init_version_router(version_repo: VersionRepo) -> APIRouter:

    version_router = APIRouter(prefix="", tags=["Version"])

    @version_router.get("/v1/versions",
                        response_model=version_schemas.VersionPaginatedResp)
    def get_versions(page: int = Query(1, ge=1),
                     size: int = Query(5, ge=1, le=5)):

        try:
            versions: List[VersionInfo] = version_repo.get_versions()
            versions = [version_schemas.VersionInfoResp(version=version.version,
                                                        upgrade_from=version.upgrade_from,
                                                        state=version.state,
                                                        started_at=version.started_at,
                                                        finished_at=version.finished_at,
                                                        builded_at=version.builded_at) for version in versions]
        except RepoInternalError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to get versions info")
    
        total = len(versions)
        start = (page - 1) * size
        end = start + size
        items = versions[start: end]

        return version_schemas.VersionPaginatedResp(total=total,
                                                    page=page,
                                                    size=size,
                                                    items=items)


    @version_router.get("/v1/versions/{version}")
    def get_version(version: str):

        try:
            version: VersionInfo = version_repo.get_version(version=version)
        except RepoInternalError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Failed to get version {version} info")

        return version_schemas.VersionInfoResp(version=version.version,
                                               upgrade_from=version.upgrade_from,
                                               state=version.state,
                                               started_at=version.started_at,
                                               finished_at=version.finished_at,
                                               builded_at=version.builded_at)
    
    # {TODO} two endpoints for upgrade

    @version_router.post("/v1/versions/upgrade/{version}")
    def trigger_upgrade():
        return status.HTTP_200_OK

    # {TODO} two endpoints for checking progress

    @version_router.get("/v1/versions/upgrade/{version}/progress")
    def get_upgrade_progress():
        return status.HTTP_200_OK

    return version_router