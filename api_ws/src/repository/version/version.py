import datetime
import structlog

from enum import Enum
from typing import List

from sqlalchemy import (
    Engine,
    select
)
from sqlalchemy.orm import sessionmaker

from sqlalchemy.dialects.postgresql import insert

from repository.version.schemas import (
    _VERSION_BASE_REPO,
    VersionInfo
)

from repository.exceptions import RepoInternalError

class UpgradedState(Enum):
    SUCCESS = "Success"
    FAIL = "Failed"

class VersionRepo:
    
    def __init__(self,
                 logger: structlog.stdlib.BoundLogger,
                 engine: Engine):
        
        # register logger
        self.logger = logger

        # register database session maker
        self.session_maker = sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine)
    
    # default setting for testing
    def init_default_versions(self):

        with self.session_maker() as session:

            try:
                started_at = datetime.datetime.now()

                insert_stmt = (
                    insert(VersionInfo)
                    .values([{"version": "1.2.8",
                              "upgrade_from": "1.2.7",
                              "state": UpgradedState.SUCCESS.value,
                              "started_at": started_at,
                              "finished_at": started_at + datetime.timedelta(seconds=10.0),
                              "builded_at": started_at - datetime.timedelta(weeks=1)},
                             {"version": "1.2.7",
                              "upgrade_from": "1.2.6",
                              "state": UpgradedState.SUCCESS.value,
                              "started_at": started_at,
                              "finished_at": started_at + datetime.timedelta(seconds=10.0),
                              "builded_at": started_at - datetime.timedelta(weeks=1)}])
                )

                do_upsert_stmt = insert_stmt.on_conflict_do_nothing(
                    index_elements=[VersionInfo.version]
                )

                session.execute(do_upsert_stmt)
                session.commit()

            except Exception as err:
                session.rollback()
                self.logger.error(f"[VersionRepo][init_default_versions] Failed to init default versions: {str(err)}")

    def get_versions(self) -> List[VersionInfo]:

        with self.session_maker() as session:

            try:
                versions_stmt = (
                    select(VersionInfo)
                    .cte("get_versions_cte")
                )

                versions = session.query(versions_stmt).all()
                return versions
            except Exception as err:
                raise RepoInternalError(f"Failed get versions: {str(err)}")


    def get_version(self, version: str) -> VersionInfo:

        with self.session_maker() as session:

            try:
                version_stmt = (
                    select(VersionInfo)
                    .where(VersionInfo.version == version)
                    .cte("get_version_cte")
                )

                version = session.query(version_stmt).one()
                return version
            except Exception as err:
                raise RepoInternalError(f"Failed get versions: {str(err)}")


def setup_version_repo(logger: structlog.stdlib.BoundLogger,
                       engine: Engine) -> VersionRepo:
    
    _VERSION_BASE_REPO.metadata.create_all(engine)

    version_repo = VersionRepo(logger=logger,
                               engine=engine)
    version_repo.init_default_versions()
    
    return version_repo