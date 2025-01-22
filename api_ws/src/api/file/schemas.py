from pydantic import BaseModel

class UploadFileProgress(BaseModel):
    upload_bytes: int