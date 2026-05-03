from pydantic import BaseModel


class UserPrepareRequest(BaseModel):
    transaction_id: str
    user_id: int
    amount: float


class BookPrepareRequest(BaseModel):
    transaction_id: str
    book_id: int
    quantity: int

class UserCommitRequest(BaseModel):
    user_id: str
    transaction_id: str

class BookCommitRequest(BaseModel):
    book_id: str
    transaction_id: str

class RollbackRequest(BaseModel):
    transaction_id: str


class PrepareResponse(BaseModel):
    transaction_id: str
    ready: bool
    reason: str | None = None

class BookPrepareResponse(PrepareResponse):
    total_price: float | None = None

class UserCommitResponse(BaseModel):
    transaction_id: str
    remaining_balance: float


class BookCommitResponse(BaseModel):
    transaction_id: str
    remaining_stock: int
