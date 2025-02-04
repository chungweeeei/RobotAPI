from sqlalchemy import func
from sqlalchemy.orm import registry

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime
)

_MAP_REPO_BASE = registry().generate_base()

class MapInfo(_MAP_REPO_BASE):
    __tablename__ = "map_info"
    map_id = Column(String, primary_key=True)
    map_name = Column(String)
    resolution = Column(Float)
    origin_pose_x = Column(Float)
    origin_pose_y = Column(Float)
    width = Column(Integer)
    height = Column(Integer)

    deployed_at = Column(DateTime(timezone=False),
                         default=func.now())

    modified_at = Column(DateTime(timezone=False),
                         nullable=True)
    

    def __repr__(self) -> str:

        return f"map_id: {self.map_id}, map_name: {self.map_name} resolution: {self.resolution}, origin_pose_x: {self.origin_pose_x}, origin_pose_y: {self.origin_pose_y}, width: {self.width}, height: {self.width}"