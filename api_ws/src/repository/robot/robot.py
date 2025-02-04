import time
import structlog

from typing import (
    List,
    Union
)

from sqlalchemy import (
    Engine,
    select
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

from repository.robot.schemas import (
    _ROBOT_REPO_BASE,
    RobotInfo,
    RobotStatus,
    LatestRobotStatus
)

class RobotRepo:

    def __init__(self, 
                 logger: structlog.stdlib.BoundLogger,
                 engine: Engine):

        # register log handler
        self.logger = logger

        # register database session maker 
        self.session_maker = sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine)
        
    def register(self, robot_info: RobotInfo):

        with self.session_maker() as session:
            
            """
                __INSERT__ statement inserts a new row into a table.

                sql insert basic syntax:
                INSERT INTO <table_name> (<column1>, <column2>, <column3>)
                VALUES (<value1>, <value2>, <value3>);
            """
            
            try:
                """
                    PostgreSQL DML insert Constructs => Create insert object

                    e.g:
                    stmt = (
                        insert(user_table).
                        values(name="user_table", fullname='Full Username)
                    )
                """

                insert_stmt = (
                    insert(RobotInfo).
                    values(robot_id=robot_info.robot_id,
                           robot_name=robot_info.robot_name,
                           registered_at=robot_info.registered_at,
                           deleted_at=robot_info.deleted_at
                    )
                )

                """
                    on conflict do update is a clause used in PostgreSQL to handle conflicts that 
                    arise during an INSERT operation. It is part of the INSERT ... ON CONFLICT statement, which
                    allow you to specify an alternative action to take when a conflict occurs, 
                    such as updating the existing row instead of throwing an error.

                    Specifies a DO UPDATE SET action for ON CONFLICT caluse.

                    Parameters:
                    - constraint: The name of unique or exclusion constraint on the table or the constraint object itself if 
                                  it has a name attribute
                    - index_elements: A sequence consisting of string column names
                    - index_where: Additional WHERE criterion that can be used to infer a conditional target index.
                    - set_: A dictionary or other mapping object where the keys are either names of columns in the target table.

                    "excluded" is a special table that contains the values proposed for insertion.
                """

                do_update_stmt = insert_stmt.on_conflict_do_update(
                    index_elements=[RobotInfo.robot_id],
                    set_={"robot_name": insert_stmt.excluded.robot_name})
    
                session.execute(do_update_stmt)
                session.commit()

            except Exception as err:
                self.logger.error("[RobotRepo][register] Failed to register: {}".format(err))
                session.rollback()

    def upsert_robot_status(self, robot_status: RobotStatus):

        with self.session_maker() as session:

            try:
                insert_stmt = (
                    insert(RobotStatus).
                    values(robot_id=robot_status.robot_id,
                           map_id=robot_status.map_id,
                           position_x=robot_status.position_x,
                           position_y=robot_status.position_y,
                           position_yaw=robot_status.position_yaw,
                           registered_at=robot_status.registered_at,
                           updated_at=robot_status.updated_at,
                           deleted_at=robot_status.deleted_at)
                )

                do_upsert_stmt = insert_stmt.on_conflict_do_update(
                    index_elements=[RobotStatus.robot_id],
                    set_={"map_id": robot_status.map_id,
                          "position_x": robot_status.position_x,
                          "position_y": robot_status.position_y,
                          "position_yaw": robot_status.position_yaw,
                          "updated_at": robot_status.updated_at
                    }
                )

                session.execute(do_upsert_stmt)
                session.commit()

            except Exception as err:
                self.logger.error("[RobotRepo][upsert_robot_status] Failed to upsert robot_status: {}".format(err))
                session.rollback()

    # def fetch_latest_robot_status(self) -> Union[None, List[LatestRobotStatus]]:

    #     with self.session_maker() as session:

    #         try:
    #             """
    #                 Query multiple tables 

    #                 in sql syntax, JOIN ... ON clause can finished this.
    #             """

    #             robot_status_stmt = (
    #                 select(
    #                     RobotInfo.robot_id,
    #                     RobotInfo.robot_name,
    #                     RobotStatus.map_id,
    #                     RobotStatus.position_x,
    #                     RobotStatus.position_y,
    #                     RobotStatus.position_yaw
    #                 )
    #                 .join(RobotStatus, RobotInfo.robot_id == RobotStatus.robot_id)
    #                 .cte("robot_status_stmt")
    #             )

    #             """
    #                 convert above query command to sql clause would be:
                    
    #                 SELECT robot_info.*, robot_status.*
    #                 FROM robot_info
    #                 JOIN robot_status
    #                     ON robot_info.robot_id = robot_status.robot_id
    #             """


    #             """
    #                 In SQLAlchemy, .cte is a method used to create a Common Table Expression(CTE).
    #                 A CTE is a temporary result set that you can reference within a SELECT, INSERT, UPDATE, or DELETE statement.
    #                 Use the CTE to join with MapInfo to get the map_name
    #             """
    #             result = (
    #                 session.query(
    #                     robot_status_stmt.c.robot_id,
    #                     robot_status_stmt.c.robot_name,
    #                     MapInfo.map_name,
    #                     robot_status_stmt.c.position_x,
    #                     robot_status_stmt.c.position_y,
    #                     robot_status_stmt.c.position_yaw
    #                 )
    #                 .join(MapInfo, robot_status_stmt.c.map_id == MapInfo.map_id)
    #                 .all()
    #             )

    #             latest_robot_status = [LatestRobotStatus(robot_id=row.robot_id,
    #                                                      robot_name=row.robot_name,
    #                                                      map_name=row.map_name,
    #                                                      position_x=row.position_x,
    #                                                      position_y=row.position_y,
    #                                                      position_yaw=row.position_yaw) for row in result]

    #             return latest_robot_status

    #         except Exception as err:
    #             self.logger.error("[RobotRepo][fetch_latest_robot_status] Failed to fetch latest robot_status: {}".format(err))
    #             session.rollback()

    def fetch_robot_name(self, robot_id: str) -> Union[None, str]:

        with self.session_maker() as session:

            try:
                """
                    query specify column

                    SELECT robot_name from robot_info
                    WHERE robot_id == argument

                    NOTE:
                    in sqlalchemy, we can use in_ function filter table by a list
                """

                row = session.query(RobotInfo.robot_name).where(RobotInfo.robot_id == robot_id).one()

                return row[0]

            except Exception as err:
                self.logger.error("[RobotRepo][fetch_robot_name] Failed to fetch {}'s robot_name: {}".format(robot_id, err))
                session.rollback()

def setup_robot_repo(logger: structlog.stdlib.BoundLogger, engine: Engine) -> RobotRepo:

    # create table in database
    _ROBOT_REPO_BASE.metadata.create_all(engine)

    # create RobotRepo instance
    robot_repo = RobotRepo(logger=logger, engine=engine)

    return robot_repo

if __name__ == "__main__":

    from settings.settings import postgres_settings
    from database.postgres import connect_to_postgres
    from helpers.time_helper import to_taipei_time

    pg_engine = connect_to_postgres(
        host=postgres_settings.host,
        port=postgres_settings.port,
        db_name=postgres_settings.db_name,
        user=postgres_settings.user,
        password=postgres_settings.password
    )

    logger = structlog.get_logger()

    robot_repo = setup_robot_repo(logger=logger,
                                  engine=pg_engine)
    
    robot_repo.register(robot_info=RobotInfo(robot_id="robot01", 
                                             robot_name="01", 
                                             registered_at=to_taipei_time(timestamp=time.time())))
    

    robot_repo.upsert_robot_status(robot_status=RobotStatus(robot_id="robot01",
                                                            map_id="map01",
                                                            position_x=0.0,
                                                            position_y=0.0,
                                                            position_yaw=0.0,
                                                            registered_at=to_taipei_time(timestamp=time.time()),
                                                            updated_at=to_taipei_time(timestamp=time.time())))
    
    robot_repo.upsert_robot_status(robot_status=RobotStatus(robot_id="robot01",
                                                            map_id="map01",
                                                            position_x=5.0,
                                                            position_y=5.0,
                                                            position_yaw=0.0,
                                                            registered_at=to_taipei_time(timestamp=time.time()),
                                                            updated_at=to_taipei_time(timestamp=time.time())))
    
    # latest_robot_status = robot_repo.fetch_latest_robot_status()

    logger.info("[RobotRepo] latest_robot_status: {}".format(latest_robot_status))

    robot_name = robot_repo.fetch_robot_name(robot_id="robot01")

    logger.info("[RobotRepo] 'robot01' robot_name: {}".format(robot_name))
