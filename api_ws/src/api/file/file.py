from fastapi import (
    APIRouter,
    status,
    HTTPException,
    Request,
    Header
)

import structlog

from repository.file import (
    FileRepo,
    FileObject,
)
from api.file.schemas import UploadFileProgress


def init_file_router(file_repo: FileRepo) -> APIRouter:

    file_router = APIRouter(prefix="", tags=["File"])

    @file_router.post("/v1/file/upload")
    async def file_upload(request: Request,
                          file_id: str = Header(..., alias="x-file-id"),
                          file_name: str = Header(..., alias="x-file-name"),
                          start_byte: int = Header(..., alias="x-start-byte")):

        # register file into upload file repo
        if not file_repo.check_file(file_id=file_id):
            file_repo.register_upload_file(file_id=file_id,
                                           file_name=file_name,
                                           start_byte=start_byte)
        # start uploading file
        async for chunk in request.stream():
            file_repo.upload(file_id=file_id, content=chunk)

        structlog.get_logger().info(f"File {file_id} have been uploaded")

        return status.HTTP_200_OK

    @file_router.get("/v1/file/upload/progress",
                     response_model=UploadFileProgress)
    def get_file_upload_bytes(file_id: str):

        try:
            upload_bytes = file_repo.get_upload_bytes(file_id=file_id)
        except Exception as err:
            structlog.get_logger().error(f"{str(err)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"File id {file_id} has not registered yet")

        return UploadFileProgress(upload_bytes=upload_bytes)

    return file_router