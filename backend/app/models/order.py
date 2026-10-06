from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import utcnow


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = {"comment": "订单主表"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键/单号")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), comment="下单用户 ID")
    status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        index=True,
        comment="状态：pending/paid/preparing/ready/completed/cancelled",
    )
    total_cents: Mapped[int] = mapped_column(Integer, default=0, comment="订单总价，单位分")
    remark: Mapped[str] = mapped_column(String(255), default="", comment="顾客备注")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, comment="下单时间"
    )

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    @property
    def username(self) -> str:
        return self.user.username if self.user else ""


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = {"comment": "订单明细（锁价快照，改菜单不影响历史单）"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键")
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), comment="所属订单 ID")
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"), comment="原菜品 ID")
    name: Mapped[str] = mapped_column(String(128), comment="下单时菜名快照")
    price_cents: Mapped[int] = mapped_column(Integer, comment="下单时单价快照，单位分")
    qty: Mapped[int] = mapped_column(Integer, comment="数量")

    order: Mapped["Order"] = relationship(back_populates="items")
