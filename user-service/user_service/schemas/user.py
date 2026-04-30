from datetime import datetime

from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    name: str
    balance: int

class UserUpdate(BaseModel):
    name: str | None = None
    balance: int | None = None

class UserOut(BaseModel):
    id: int
    name: str
    balance: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes = True
    )
