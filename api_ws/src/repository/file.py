import structlog
import time

from dataclasses import dataclass
from io import BytesIO
from threading import Lock

from repository.exceptions import RepoInternalError

@dataclass
class FileObject:

    name: str
    start_byte: int
    content: bytes

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

    def register_upload_file(self, file_id: str, file_name: str, start_byte: int) -> None:

        if file_id in self._upload_files:
            self.logger.info(f"[FileRepo] File ID: {file_id} already registered")
            return

        self._upload_files.update({file_id: FileObject(name=file_name, start_byte=start_byte, content=BytesIO())})

    def upload(self, file_id: str, content: bytes) -> None:

        with self._upload_lock:
            self._upload_files[file_id].content.write(content)

    def get_upload_bytes(self, file_id: str):

        if file_id not in self._upload_files:
            raise RepoInternalError(f"Failed to fetch {file_id} upload progress")

        with self._upload_lock:
            return self._upload_files[file_id].content.getbuffer().nbytes

def setup_file_repo(logger: structlog.stdlib.BoundLogger) -> FileRepo:

    file_repo = FileRepo(logger=logger)

    return file_repo