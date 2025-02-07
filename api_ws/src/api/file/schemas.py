from typing import List
from pydantic import (
    BaseModel,
    Field
)

class UploadFileProgress(BaseModel):
    uploaded_byte: int

class UpgradeArchivesResp(BaseModel):
    archives: List[str] = Field(default_factory=list)