from typing import List

from fastapi import (
    APIRouter,
    HTTPException,
    status
)

from repository.version.version import VersionRepo
from repository.version.schemas import VersionInfo
from repository.exceptions import RepoInternalError

from api.version import schemas as version_schemas

def init_version_router(version_repo: VersionRepo) -> APIRouter:

    version_router = APIRouter(prefix="", tags=["Version"])

    @version_router.get("/v1/versions",
                        response_model=version_schemas.VersionsInfo)
    def get_versions():

        try:
            versions: List[VersionInfo] = version_repo.get_versions()
        except RepoInternalError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to get versions info")
    
        return version_schemas.VersionsInfo(current_version=versions[0].version,
                                            versions=[version_schemas.VersionInfo(version=version.version,
                                                                                  upgrade_from=version.upgrade_from,
                                                                                  state=version.state,
                                                                                  started_at=version.started_at,
                                                                                  finished_at=version.finished_at,
                                                                                  builded_at=version.builded_at) for version in versions])

    @version_router.get("/v1/versions/{version}")
    def get_version(version: str):

        try:
            version: VersionInfo = version_repo.get_version(version=version)
        except RepoInternalError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Failed to get version {version} info")

        return version_schemas.VersionInfo(version=version.version,
                                           upgrade_from=version.upgrade_from,
                                           state=version.state,
                                           started_at=version.started_at,
                                           finished_at=version.finished_at,
                                           builded_at=version.builded_at)

    return version_router