from pydantic import BaseModel

class SystemSettingsResp(BaseModel):

    robot_id: str = "robot1"
    robot_name: str = "robot1"

    map: str = "test"
    initial_pose_x: float = 0.0
    initial_pose_y: float = 0.0
    initial_pose_yaw: float = 0.0

class SettingsResp(BaseModel):

    system: SystemSettingsResp = SystemSettingsResp()

class TestReq(BaseModel):

    category: str
    settings: str