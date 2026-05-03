from fastapi import FastAPI

from common.app import create_base_app
from book_service.routes import books, purchase

app = create_base_app()
app.include_router(books.router)
app.include_router(purchase.router)
