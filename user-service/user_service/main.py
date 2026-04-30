from fastapi import FastAPI

from user_service.routes import users
from user_service.middlewares.logging import logging_middleware

app = FastAPI()

app.include_router(users.router)

app.middleware("http")(logging_middleware)
