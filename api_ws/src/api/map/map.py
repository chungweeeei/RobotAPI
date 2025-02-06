import structlog

from fastapi import (
    APIRouter,
    status,
    Depends,
    HTTPException
)

from typing import (
    List,
    Union,
    Annotated
)

from dependecy.dependencies import extract_bind_logger

from repository.map.map import MapRepo
from repository.map.schemas import MapInfo
from repository.exceptions import RepoInternalError

from api.map import schemas as map_schemas

def init_map_router(map_repo: MapRepo) -> APIRouter:

    map_router = APIRouter(prefix="", tags=["Map"])


    @map_router.get("/v1/maps",
                    response_model=map_schemas.MapsInfoResp)
    def get_maps(logger=Depends(extract_bind_logger)):
        
        try:
            maps_info: List[MapInfo] = map_repo.fetch_maps()
        except RepoInternalError as err:
            logger.error(f"Failed to fetch maps: {str(err)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to fetch maps")

        return map_schemas.MapsInfoResp(maps=[map_schemas.MapInfo(map_id=map.map_id,
                                                                  map_name=map.map_name,
                                                                  resolution=map.resolution,
                                                                  origin_pose_x=map.origin_pose_x,
                                                                  origin_pose_y=map.origin_pose_y,
                                                                  width=map.width,
                                                                  height=map.height) for map in maps_info])
    
    @map_router.post("/v1/maps")
    def deploy_map(map: map_schemas.MapInfo,
                   logger=Depends(extract_bind_logger)):

        try:
            map_repo.deploy_maps(maps_info=[MapInfo(map_id=map.map_id,
                                                    map_name=map.map_name,
                                                    resolution=map.resolution,
                                                    origin_pose_x=map.origin_pose_x,
                                                    origin_pose_y=map.origin_pose_y,
                                                    width=map.width,
                                                    height=map.height)])
        except RepoInternalError as err:
            logger.error(f"Failed to deploy map: {map}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return status.HTTP_201_CREATED

    @map_router.get("/v1/maps/{map_id}",
                    response_model=map_schemas.MapInfo)
    def get_map(map_id: str,
                logger=Depends(extract_bind_logger)):

        try:
            map_info: MapInfo = map_repo.fetch_map(map_id=map_id)
        except RepoInternalError as err:
            logger.error(f"Failed to fetch map: {map_id}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Failed to fetch map {map_id}")

        return map_schemas.MapInfo(map_id=map_info.map_id,
                                   map_name=map_info.map_name,
                                   resolution=map_info.resolution,
                                   origin_pose_x=map_info.origin_pose_x,
                                   origin_pose_y=map_info.origin_pose_y,
                                   width=map_info.width,
                                   height=map_info.height)

    # @map_router.put("/v1/maps/{map_id}")
    # def get_map(map_id: str,
    #             logger=Depends(extract_bind_logger)):

    #     try:
    #         map_info: MapInfo = map_repo.fetch_map(map_id=map_id)
    #     except RepoInternalError as err:
    #         logger.error(f"Failed to fetch map: {map_id}")
    #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #                             detail=f"Failed to fetch map {map_id}")
        
    #     return status.HTTP_200_OK

    return map_router