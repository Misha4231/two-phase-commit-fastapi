from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BookCreate(BaseModel):
    title: str
    author: str
    stock: int
    price: float


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    stock: int | None = None
    price: float | None = None


class BookOut(BaseModel):
    id: int
    title: str
    author: str
    stock: int
    price: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
