from typing import List

from datetime import datetime
from pydantic import BaseModel

from task.upgrade import UpgradeState


class VersionInfoResp(BaseModel):
    version: str
    upgrade_from: str
    state: str
    started_at: datetime
    finished_at: datetime
    builded_at: datetime

class VersionsInfoResp(BaseModel):
    current_version: str
    versions: List[VersionInfoResp]

class VersionPaginatedResp(BaseModel):
    total: int # Total number of items
    page: int # Current Page number
    size: int # Number of items per page
    versions: List[VersionInfoResp] # List of items on the current page

class UpgradeProgressResp(BaseModel):
    state: UpgradeState
    message: str = "Default Status"
