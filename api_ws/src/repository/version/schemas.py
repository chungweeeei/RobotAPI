from sqlalchemy import (
    Column,
    String,
    DateTime,
    func
)

from sqlalchemy.orm import registry

_VERSION_BASE_REPO = registry().generate_base()

class VersionInfo(_VERSION_BASE_REPO):
    __tablename__ = "version_info"
    version = Column(String, primary_key=True)
    upgrade_from = Column(String)
    state = Column(String)
    started_at = Column(DateTime(timezone=False),
                        default=func.now())
    finished_at = Column(DateTime(timezone=False),
                         nullable=True)
    builded_at = Column(DateTime(timezone=False),
                        nullable=True)