# 让 from app.routers import auth 能找到子模块。
from app.routers import auth, cart, dishes, orders

__all__ = ["auth", "cart", "dishes", "orders"]
