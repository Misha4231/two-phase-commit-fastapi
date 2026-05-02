from common.app import create_base_app
from coordinator.routes import orders

app = create_base_app()
app.include_router(orders.router)
