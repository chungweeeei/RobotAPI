import structlog

from typing import List

from sqlalchemy import (
    Engine,
    select
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

from repository.map.schemas import (
    _MAP_REPO_BASE,
    MapInfo
)
from repository.exceptions import RepoInternalError

class MapRepo:

    def __init__(self, 
                 logger: structlog.stdlib.BoundLogger,
                 engine: Engine):

        # register log handler
        self.logger = logger

        # register database session maker
        self.session_maker = sessionmaker(autoflush=False,
                                          autocommit=False,
                                          bind=engine)

    def deploy_maps(self, maps_info: List[MapInfo]):

        with self.session_maker() as session:

            try:
                insert_stmt = (
                    insert(MapInfo).
                    values([{"map_id": map_info.map_id,
                             "map_name": map_info.map_name,
                             "resolution": map_info.resolution,
                             "origin_pose_x": map_info.origin_pose_x,
                             "origin_pose_y": map_info.origin_pose_y,
                             "width": map_info.width,
                             "height": map_info.height} for map_info in maps_info])
                )

                # do_update_stmt = insert_stmt.on_conflict_do_update(
                #     index_elements=[MapInfo.map_id],
                #     set_={"map_name": insert_stmt.excluded.map_name,
                #           "resolution": insert_stmt.excluded.resolution,
                #           "origin_pose_x": insert_stmt.excluded.origin_pose_x,
                #           "origin_pose_y": insert_stmt.excluded.origin_pose_y,
                #           "width": insert_stmt.excluded.width,
                #           "height": insert_stmt.excluded.height}
                # )

                session.execute(insert_stmt)
                session.commit()

            except Exception as err:
                session.rollback()
                raise RepoInternalError(f"Failed to deploy maps: {str(err)}")

    def fetch_maps(self) -> List[MapInfo]:

        with self.session_maker() as session:

            try:
                maps_info_stmt = (
                    select(MapInfo)
                    .cte("maps_info_cte")
                )

                maps_info = session.query(maps_info_stmt).all()
                return maps_info
            except Exception as err:
                session.rollback()
                raise RepoInternalError(str(err))

    def fetch_map(self, map_id: str) -> MapInfo:

        with self.session_maker() as session:

            try:
                map_info_stmt = (
                    select(MapInfo)
                    .where(MapInfo.map_id == map_id)
                    .cte("map_info_cte")
                )

                map_info = session.query(map_info_stmt).one()
                return map_info
            except Exception as err:
                session.rollback()
                raise RepoInternalError(str(err))


def setup_map_repo(logger: structlog.stdlib.BoundLogger,
                   engine: Engine) -> MapRepo:

    _MAP_REPO_BASE.metadata.create_all(engine)

    map_repo = MapRepo(logger=logger, engine=engine)

    return map_repo

if __name__ == "__main__":

    from settings.settings import postgres_settings
    from database.postgres import connect_to_postgres

    pg_engine = connect_to_postgres(
        host=postgres_settings.host,
        port=postgres_settings.port,
        db_name=postgres_settings.db_name,
        user=postgres_settings.user,
        password=postgres_settings.password
    )

    logger = structlog.get_logger()

    map_repo = setup_map_repo(logger=logger, engine=pg_engine)

    map_repo.deploy_maps(maps_info=[MapInfo(map_id="map01",
                                           map_name="test_map01",
                                           resolution=0.03,
                                           origin_pose_x=0.0,
                                           origin_pose_y=0.0,
                                           width=640,
                                           height=640),
                                    MapInfo(map_id="map02",
                                            map_name="test_map02",
                                            resolution=0.03,
                                            origin_pose_x=0.0,
                                            origin_pose_y=0.0,
                                            width=320,
                                            height=320)])