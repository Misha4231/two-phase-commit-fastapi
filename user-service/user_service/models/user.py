from sqlalchemy import Column, Integer, DECIMAL, String

from common.models.base import TimeStampedModel


class User(TimeStampedModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    balance = Column(DECIMAL(8, 2), default=0)
