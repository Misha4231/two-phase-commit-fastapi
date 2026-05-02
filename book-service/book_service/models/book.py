from sqlalchemy import Column, Integer, String, DECIMAL

from common.models.base import TimeStampedModel


class Book(TimeStampedModel):
    __tablename__ = "books"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    author = Column(String(100), nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    price = Column(DECIMAL(8, 2), nullable=False)
