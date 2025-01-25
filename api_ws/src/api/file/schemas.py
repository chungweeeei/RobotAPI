from pydantic import BaseModel

class UploadFileProgress(BaseModel):
    uploaded_byte: int