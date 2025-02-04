import structlog

from io import BytesIO
from threading import Lock
from dataclasses import dataclass

from repository.exceptions import RepoInternalError

@dataclass
class FileObject:

    name: str
    start_byte: int
    content: BytesIO

class FileRepo:

    def __init__(self, logger: structlog.stdlib.BoundLogger):

        # register log handler
        self.logger = logger

        # register upload file
        self._upload_files = {}

        # register lock
        self._upload_lock = Lock()

    def check_file(self, file_id: str) -> bool:

        return True if file_id in self._upload_files else False

    def register_upload_file(self, file_id: str, file_obj: FileObject) -> None:

        if file_id in self._upload_files:
            self.logger.info(f"[FileRepo][register_upload_file] File ID: {file_id} already registered")
            return

        self._upload_files.update({file_id: file_obj})

    def upload(self, file_id: str, content: bytes) -> None:

        with self._upload_lock:
            self._upload_files[file_id].content.write(content)

    def get_uploaded_byte(self, file_id: str) -> int:

        if file_id not in self._upload_files:
            raise RepoInternalError(f"File[{file_id}] has not been registered")

        with self._upload_lock:
            return self._upload_files[file_id].content.getbuffer().nbytes

    def deploy(self, file_id: str) -> None:

        with self._upload_lock:

            file_obj = self._upload_files[file_id]
            file_obj.content.seek(0)

            with open(file_obj.name, "wb") as file:
                file.write(file_obj.content.read())

        self.logger.info(f"[FileRepo][deploy] {file_obj.name} have been deployed, start to clear local cache data")

        '''
            remove local-cache memory in file content
            BytesIO.seek(0) -> move the cursor to the beginning of the file
            BytesIO.truncate(0) -> clear the streaming content size
        '''
        file_obj.content.seek(0)
        file_obj.content.truncate(0)

        with self._upload_lock:
            del self._upload_files[file_id]

        self.logger.info(f"[FileRepo][deploy] {file_obj.name} local cache data have been cleared")

def setup_file_repo(logger: structlog.stdlib.BoundLogger) -> FileRepo:

    file_repo = FileRepo(logger=logger)

    return file_repo