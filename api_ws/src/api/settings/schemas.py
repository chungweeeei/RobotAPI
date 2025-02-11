from pydantic import BaseModel

class SystemSettings(BaseModel):

    robot_name: str = "robot1"

    map: str = "test"
    initial_pose_x: float = 0.0
    initial_pose_y: float = 0.0
    initial_pose_yaw: float = 0.0

class MoveSettings(BaseModel):

    max_linear_speed: float = 1.0
    max_angular_speed: float = 0.3


class SettingsResp(BaseModel):

    system: SystemSettings = SystemSettings()
    move: MoveSettings = MoveSettings()