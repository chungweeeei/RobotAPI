import structlog
import threading

from repository.setting.schemas import (
    SystemSettings,
    MoveSettings
)

from repository.exceptions import RepoInternalError

class SettingRepo:
    
    def __init__(self, logger: structlog.stdlib.BoundLogger):

        # register log handler
        self.logger = logger

        # init default settings
        self.init_default_settings()

        # regsiter setting lock
        self._settings_lock = threading.Lock()

    def init_default_settings(self):

        self._system_settings = SystemSettings(robot_name="robot01",
                                               map="test1",
                                               initial_pose_x=0.0,
                                               initial_pose_y=0.0,
                                               initial_pose_yaw=0.0)
        
        self._move_settings = MoveSettings(max_linear_speed=1.0,
                                           max_angular_speed=0.3)
        
    def get_system_settings(self) -> SystemSettings:

        with self._settings_lock:
            return self._system_settings
        
    def get_move_settings(self) -> MoveSettings:

        with self._settings_lock:
            return self._move_settings
        
    def set_system_settings(self, settings: SystemSettings):

        with self._settings_lock:
            try:
                self._system_settings = settings
            except Exception:
                raise RepoInternalError("Failed to set system settings")

    def set_move_settings(self, settings: MoveSettings):

        with self._settings_lock:
            try:
                self._move_settings = settings
            except Exception:
                raise RepoInternalError("Failed to set move settings")


def setup_setting_repo(logger: structlog.stdlib.BoundLogger) -> SettingRepo:

    setting_repo = SettingRepo(logger=logger)

    return setting_repo