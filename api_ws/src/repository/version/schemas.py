import datetime
from enum import Enum
from typing import List

from sqlalchemy import (
    Column,
    String,
    DateTime,
    func
)

from sqlalchemy.orm import registry

_VERSION_BASE_REPO = registry().generate_base()

class VersionInfo(_VERSION_BASE_REPO):
    __tablename__ = "version_info"
    version = Column(String, primary_key=True)
    upgrade_from = Column(String)
    state = Column(String)
    started_at = Column(DateTime(timezone=False),
                        default=func.now())
    finished_at = Column(DateTime(timezone=False),
                         nullable=True)
    builded_at = Column(DateTime(timezone=False),
                        nullable=True)
    
class UpgradeResp(Enum):
    SUCCESS = "Success"
    FAIL = "Failed"

# Version Factory
def generate_test_versions(num_version: int) -> List:

    started_at = datetime.datetime.now()

    versions = [{"version": f"1.2.{i+1}",
                 "upgrade_from": f"1.2.{i}",
                 "state": UpgradeResp.SUCCESS.value,
                 "started_at": (started_at - datetime.timedelta(seconds=30 * (num_version - i))),
                 "finished_at": (started_at - datetime.timedelta(seconds=30 * (num_version - i))) + datetime.timedelta(seconds=10),
                 "builded_at": (started_at - datetime.timedelta(seconds=30 * (num_version - i))) - datetime.timedelta(weeks=1)} for i in range(num_version)]
    
    return versions
          
