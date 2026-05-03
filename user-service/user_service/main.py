from common.app import create_base_app
from user_service.routes import users, purchase

app = create_base_app()
app.include_router(users.router)
app.include_router(purchase.router)
