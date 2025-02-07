import time
import threading
import structlog

from enum import Enum

class UpgradeState(Enum):
    DEFAULT = "default"
    CHECK = "check"
    BACKUP = "backup"
    GENERATE = "generate"
    CLEAN = "clean"
    INSTALL = "install"
    RESTART = "restart"


class UpgradeTask:

    def __init__(self, logger: structlog.stdlib.BoundLogger):

        # register log handler
        self.logger = logger

        # register default upgrade state
        self._upgrade_progress = UpgradeState.DEFAULT

        # register a threadling Lock
        self._upgrade_lock = threading.Lock()

    def upgrade(self):

        for state in UpgradeState:

            time.sleep(3.0)

            with self._upgrade_lock:
                self._upgrade_progress = state
            
            self.logger.info("[UpgradeTaske][upgrade] Current upgrade progress: {}".format(self._upgrade_progress.value))

    def get_upgrade_progress(self) -> UpgradeState:

        with self._upgrade_lock:
            return self._upgrade_progress

def setup_upgrade_task(logger: structlog.stdlib.BoundLogger) -> UpgradeTask:

    upgrade_task = UpgradeTask(logger=logger)
    upgrade_task_thread = threading.Thread(target=upgrade_task.upgrade, daemon=True)
    upgrade_task_thread.start()

    return upgrade_task

if __name__ == "__main__":

    upgrade_task = setup_upgrade_task(logger=structlog.get_logger())