from fastapi import (
    APIRouter,
    status,
    HTTPException,
    Request,
    Header
)

import structlog
from io import BytesIO

from repository.file.file import (
    FileRepo,
    FileObject,
)

from api.file import schemas as file_schemas 

from starlette.requests import ClientDisconnect


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
                                           file_obj=FileObject(name=file_name,
                                                               start_byte=start_byte,
                                                               content=BytesIO()))

        # start uploading file {TODO} need to testing mulitple file uploading...
        try:
            async for chunk in request.stream():
                file_repo.upload(file_id=file_id, content=chunk)
        except ClientDisconnect:
            structlog.get_logger().info(f"Client has disconnected, File[{file_id}] have been uploaded {file_repo.get_uploaded_byte(file_id=file_id)} bytes")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Client has disconnected")
        except Exception as err:
            structlog.get_logger().error(f"{str(err)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Internal server error")

        structlog.get_logger().info(f"File {file_id} have been uploaded")

        file_repo.deploy(file_id=file_id)

        return status.HTTP_200_OK

    @file_router.get("/v1/file/upload/progress",
                     response_model=file_schemas.UploadFileProgress)
    def get_file_uploaded_byte(file_id: str):

        try:
            uploaded_byte = file_repo.get_uploaded_byte(file_id=file_id)
        except Exception as err:
            structlog.get_logger().warn(f"{str(err)}")
            return file_schemas.UploadFileProgress(uploaded_byte=0)

        return file_schemas.UploadFileProgress(uploaded_byte=uploaded_byte)
    

    @file_router.get("/v1/file/upgrade/archives",
                     response_model=file_schemas.UpgradeArchivesResp)
    def get_version_archives():
            
        archives = file_repo.get_upgrade_versions_archives()

        return file_schemas.UpgradeArchivesResp(archives=archives)


    # {TODO} provide a endpoint which send the streaming response

    return file_router