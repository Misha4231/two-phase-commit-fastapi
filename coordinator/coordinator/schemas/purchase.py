from pydantic import BaseModel


class PurchaseRequest(BaseModel):
    book_id: int
    user_id: int
    quantity: int = 1


class PurchaseResponse(BaseModel):
    user_id: int
    book_id: int
    quantity: int
    total_price: float
    remaining_balance: float
    remaining_stock: int
