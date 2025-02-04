from pydantic import BaseModel

class SystemSettingsResp(BaseModel):

    robot_id: str = "robot1"
    robot_name: str = "robot1"

    map: str = "test"
    initial_pose_x: float = 0.0
    initial_pose_y: float = 0.0
    initial_pose_yaw: float = 0.0

# class SystemSettingReq(BaseModel):    

class MoveSettingsResp(BaseModel):

    max_linear_speed: float = 1.0
    max_angular_speed: float = 0.3


class SettingsResp(BaseModel):

    system: SystemSettingsResp = SystemSettingsResp()
    move: MoveSettingsResp = MoveSettingsResp()