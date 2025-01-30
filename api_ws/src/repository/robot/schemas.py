from pydantic import (
    Field,
    BaseModel
)

class LatestRobotStatus(BaseModel):
    robot_id: str = Field(..., examples="robot01", description="robot unique id")
    robot_name: str = Field(..., examples="01", description="user-defined robot name")
    map_name: str = Field(..., examples="test", description="running map")
    position_x: float = Field(..., examples=0.0, description="robot x position")
    position_y: float = Field(..., examples=0.0, description="robot y position")
    position_yaw: float = Field(..., examples=0.0, description="robot yaw position")