import datetime
import structlog
from threading import Lock
from functools import lru_cache

from typing import List

from sqlalchemy import (
    Engine,
    select
)
from sqlalchemy.orm import sessionmaker

from sqlalchemy.dialects.postgresql import insert

from repository.version.schemas import (
    _VERSION_BASE_REPO,
    VersionInfo,
    UpgradeResp,
    generate_test_versions
)

from repository.exceptions import (
    RepoInternalError,
    BadRequestError
)

from task.upgrade import (
    UpgradeState,
    setup_upgrade_task
)


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
        
        # register upgrade state
        self._upgrade_tasks_lock = Lock()
        self._upgrade_tasks = {}

        # regsite default latest_version
        self._latest_version = "0.0.0"

    # default setting for testing
    def init_default_versions(self):

        with self.session_maker() as session:

            try:
                
                insert_stmt = (
                    insert(VersionInfo)
                    .values(generate_test_versions(num_version=10))
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
                    .order_by(VersionInfo.started_at.desc())
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

    def get_latest_version(self):

        try:
            latest_version = self.get_versions()[0]
            self._current_version = latest_version.version
        except Exception:
            pass

    def trigger_upgrade(self, version: str):

        if version in self._upgrade_tasks:
            raise BadRequestError(f"system upgrade to version {version} now")
        
        upgrade_task = setup_upgrade_task(logger=self.logger)
        self._upgrade_tasks.update({version: upgrade_task})
        
    def get_upgrade_progress(self, version: str) -> UpgradeState:

        if version not in self._upgrade_tasks:
            raise BadRequestError(f"Has not trigger upgrade version {version} yet")
    
        return self._upgrade_tasks[version].get_upgrade_progress()

    def reset_upgrade_tasks(self, version: str):

        ## assume task to the restart state
        with self._upgrade_tasks_lock:
            try:
                del self._upgrade_tasks[version]
            except Exception as err:
                self.logger.error(f"[VersionRepo][reset_upgrade_tasks] Failed to remove upgrade to {version} version task")
                pass

        try:
            with self.session_maker() as session:

                started_at = datetime.datetime.now() 
                
                insert_stmt = (
                    insert(VersionInfo)
                    .values([{"version": version,
                              "upgrade_from": self._current_version,
                              "state": UpgradeResp.SUCCESS.value,
                              "started_at": started_at  - datetime.timedelta(seconds=30.0),
                              "finished_at": started_at,
                              "builded_at": started_at - datetime.timedelta(weeks=1)}])
                )

                do_upsert_stmt = insert_stmt.on_conflict_do_nothing(
                    index_elements=[VersionInfo.version]
                )

                session.execute(do_upsert_stmt)
                session.commit()

        except Exception as err:
            session.rollback()
            self.logger.error("[VersionRepo][reset_upgrade_tasks] Reset upgrade tasks failed: {}".format(err))
            pass


def setup_version_repo(logger: structlog.stdlib.BoundLogger,
                       engine: Engine) -> VersionRepo:
    
    _VERSION_BASE_REPO.metadata.create_all(engine)

    version_repo = VersionRepo(logger=logger,
                               engine=engine)
    version_repo.init_default_versions()
    version_repo.get_latest_version()
    
    return version_repo