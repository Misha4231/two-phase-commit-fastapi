from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

from common.models.base import Model

class TimeStampedModel(Model):
    __abstract__ = True

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
