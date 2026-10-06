from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import utcnow


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("user_id", "dish_id", name="uk_cart_user_dish"),
        {"comment": "购物车：同一用户同一道菜只有一行"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, comment="用户 ID")
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"), comment="菜品 ID")
    qty: Mapped[int] = mapped_column(Integer, default=1, comment="数量")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, comment="最近修改时间"
    )

    user: Mapped["User"] = relationship(back_populates="cart_items")
    dish: Mapped["Dish"] = relationship(back_populates="cart_items")
