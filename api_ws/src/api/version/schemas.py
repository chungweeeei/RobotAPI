from typing import List

from datetime import datetime
from pydantic import BaseModel

class VersionInfo(BaseModel):
    version: str
    upgrade_from: str
    state: str
    started_at: datetime
    finished_at: datetime
    builded_at: datetime

class VersionsInfo(BaseModel):
    current_version: str
    versions: List[VersionInfo]