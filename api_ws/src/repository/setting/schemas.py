from dataclasses import dataclass

@dataclass
class SystemSettings:
    robot_name: str
    map: str
    initial_pose_x: float = 0.0
    initial_pose_y: float = 0.0
    initial_pose_yaw: float = 0.0


@dataclass
class MoveSettings:
    max_linear_speed: float = 1.0  # unit: (m/s)
    max_angular_speed: float = 0.3 # unit: (rad/s)