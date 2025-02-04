from typing import List
from pydantic import (
    BaseModel,
    Field,
    model_validator
)

class MapInfo(BaseModel):
    map_id: str = "map03"
    map_name: str = "test_map03"
    resolution: float = 0.03
    origin_pose_x: float = 0.0
    origin_pose_y: float = 0.0
    width: int = Field(..., description="map image width, value must be greater than zero")
    height: int = Field(..., description="map image height, value must be greater than zero")

    @model_validator(mode="after")
    def _validate(self):
        if (self.width < 0.0 or self.height < 0.0):
            raise ValueError("map height/width can not be negative")

        return self

class MapsInfoResp(BaseModel):
    maps: List[MapInfo]