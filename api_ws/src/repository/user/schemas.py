from sqlalchemy import (
    Column,
    String,
    DateTime
)

from sqlalchemy.sql import func
from sqlalchemy.orm import registry

_USER_BASE_REPO = registry().generate_base()

class UserInfo(_USER_BASE_REPO):
    __tablename__ = "user_info"
    user_id = Column(String, primary_key=True)
    user_name = Column(String)
    user_role = Column(String)
    hashed_password = Column(String)
    registered_at = Column(DateTime(timezone=False),
                           default=func.now())
    
    # Combine primary key?