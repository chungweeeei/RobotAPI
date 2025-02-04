import structlog

from typing import List

from sqlalchemy import (
    Engine,
    select
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

from repository.user.schemas import (
    _USER_BASE_REPO,
    UserInfo
)

from repository.exceptions import RepoInternalError

from security.securities import generate_hashed_password

class UserRepo:

    def __init__(self,
                 logger: structlog.stdlib.BoundLogger,
                 engine: Engine):
        
        # regsiter logger
        self.logger = logger

        # # register session maker
        self.session_maker = sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine)

    def init_private_users(self):

        private_users = [UserInfo(user_id="root",
                                  user_name="root",
                                  user_role="root",
                                  hashed_password=generate_hashed_password(password="root")),
                         UserInfo(user_id="admin",
                                  user_name="admin",
                                  user_role="admin",
                                  hashed_password=generate_hashed_password(password="admin"))]

        with self.session_maker() as session:

            try:
                insert_stmt = (
                    insert(UserInfo)
                    .values([{"user_id": user.user_id,
                              "user_name": user.user_name,
                              "user_role": user.user_role,
                              "hashed_password": user.hashed_password} for user in private_users])
                )

                do_upsert_stmt = insert_stmt.on_conflict_do_nothing(
                    index_elements=[UserInfo.user_id],
                )

                session.execute(do_upsert_stmt)
                session.commit()

            except Exception as err:
                session.rollback()
                self.logger.error("[UserRepo][init_private_users] Failed to init private users: {}".format(err))
    
    def register_user(self, user_id: str, user_name: str, password: str):

        with self.session_maker() as session:

            try:
                insert_stmt = (
                    insert(UserInfo)
                    .values({"user_id": user_id,
                             "user_name": user_name,
                             "user_role": "general",
                             "hashed_password": generate_hashed_password(password)})
                )

                do_upsert_stmt = insert_stmt.on_conflict_do_update(
                    index_elements=[UserInfo.user_id],
                    set_={"user_id": insert_stmt.excluded.user_id,
                          "user_name": insert_stmt.excluded.user_name,
                          "hashed_password": insert_stmt.excluded.hashed_password}
                )

                session.execute(do_upsert_stmt)
                session.commit()

            except Exception as err:
                self.logger.error(f"{str(err)}")
                session.rollback()
                raise RepoInternalError(f"Failed to register new user: {str(err)}")
    
    def get_users(self) -> List[UserInfo]:

        with self.session_maker() as session:
        
            try:
                
                users_info_stmt = (
                    select(UserInfo)
                    .cte("users_info_stmt")
                )

                user_info = session.query(users_info_stmt).all()
                return user_info

            except Exception as err:
                session.rollback()
                raise RepoInternalError(f"Failed to get all users info: {str(err)}")
        
    def get_user(self, user_id: str) -> UserInfo:

        with self.session_maker() as session:

            try:
                
                user_info_stmt = (
                    select(UserInfo)
                    .where(UserInfo.user_id == user_id)
                    .cte("user_info_stmt")
                )

                user_info = session.query(user_info_stmt).one()
                return user_info

            except Exception as err:
                session.rollback()
                raise RepoInternalError(f"Failed to get {user_id} user info: {str(err)}")
        

def setup_user_repo(logger: structlog.stdlib.BoundLogger,
                    engine: Engine) -> UserRepo:
    
    _USER_BASE_REPO.metadata.create_all(engine)

    user_repo = UserRepo(logger=logger, engine=engine)
    user_repo.init_private_users()

    return user_repo