from sqlalchemy import Column, Integer, String

from common.models.base import TimeStampedModel


class User(TimeStampedModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    balance = Column(Integer, default=0)
