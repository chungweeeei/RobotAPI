from sqlalchemy import (
    Column,
    String,
    DateTime,
    event
)

from sqlalchemy.sql import func
from sqlalchemy.orm import registry

from repository.user.utils import (
    delete_user_func,
    delete_user_trigger
)

_USER_BASE_REPO = registry().generate_base()

class UserInfo(_USER_BASE_REPO):
    __tablename__ = "user_info"
    user_id = Column(String, primary_key=True)
    user_name = Column(String)
    user_role = Column(String)
    hashed_password = Column(String)
    registered_at = Column(DateTime(timezone=False),
                           default=func.now())

class UserInfoDeletect(_USER_BASE_REPO):
    __tablename__ = "user_info_deleted"
    user_id = Column(String, primary_key=True)
    user_name = Column(String)
    user_role = Column(String)
    deleted_at = Column(DateTime(timezone=False),
                        default=func.now())
    

event.listen(UserInfo.__table__, "after_create", delete_user_func.execute_if(dialect="postgresql"))
event.listen(UserInfo.__table__, "after_create", delete_user_trigger.execute_if(dialect="postgresql"))