from pydantic import (
    Field,
    BaseModel
)

from sqlalchemy.sql import func
from sqlalchemy.orm import registry

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
)

_ROBOT_REPO_BASE = registry().generate_base()

class RobotInfo(_ROBOT_REPO_BASE):
    __tablename__ = "robot_info"
    robot_id = Column(String, primary_key=True)
    robot_name = Column(String)

    registered_at = Column(DateTime(timezone=None),
                           default=func.now())

    deleted_at = Column(DateTime(timezone=None),
                        nullable=True)
    
    def __repr__(self) -> str:

        return f"robot_id: {self.robot_id}, robot_name: {self.robot_name}, registered_at: {self.registered_at}"

class RobotStatus(_ROBOT_REPO_BASE):
    __tablename__ = "robot_status"
    robot_id = Column(String, primary_key=True)
    map_id = Column(String)
    position_x = Column(Float)
    position_y = Column(Float)
    position_yaw = Column(Float)

    registered_at = Column(DateTime(timezone=None),
                           default=func.now())

    updated_at = Column(DateTime(timezone=None),
                        default=func.now(),
                        onupdate=func.now())

    deleted_at = Column(DateTime(timezone=None),
                        nullable=True)
    
    def __repr__(self) -> str:

        return f"robot_id: {self.robot_id}, map_id: {self.map_id}, position_x: {self.position_x}, position_y: {self.position_y}, position_yaw: {self.position_yaw}, registered_at: {self.registered_at}, updated_at: {self.updated_at}"

class LatestRobotStatus(BaseModel):
    robot_id: str = Field(..., examples="robot01", description="robot unique id")
    robot_name: str = Field(..., examples="01", description="user-defined robot name")
    map_name: str = Field(..., examples="test", description="running map")
    position_x: float = Field(..., examples=0.0, description="robot x position")
    position_y: float = Field(..., examples=0.0, description="robot y position")
    position_yaw: float = Field(..., examples=0.0, description="robot yaw position")