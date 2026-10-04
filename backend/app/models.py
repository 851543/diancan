"""
数据库实体（表结构）。
Java 对照：@Entity 类。Mapped / mapped_column ≈ @Column。
relationship ≈ @OneToMany / @ManyToOne。
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    """给 created_at 默认值用。每次插入新行时调用。"""
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"  # 真实表名。Java：@Table(name = "users")

    # Mapped[int]：这个字段在 Python 里是 int。mapped_column：对应数据库列。
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), default="customer")  # customer | admin
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # 一个用户有多张订单。list["Order"] 里的引号：Order 类写在后面，先当字符串引用。
    # back_populates="user"：和 Order.user 互指。
    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    cart_items: Mapped[list["CartItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Dish(Base):
    __tablename__ = "dishes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    category: Mapped[str] = mapped_column(String(64), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    # 金额用「分」存整数，避免 0.1+0.2 这种浮点误差。展示时 /100 才是元。
    price_cents: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[str] = mapped_column(String(512), default="")
    is_on: Mapped[int] = mapped_column(Integer, default=1)  # 1 上架 0 下架
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="dish")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # 外键，类似 @JoinColumn
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    total_cents: Mapped[int] = mapped_column(Integer, default=0)
    remark: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="orders")
    # cascade="all, delete-orphan"：删订单时，明细行一起删。
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    """订单明细。下单时把当时的菜名、单价拷一份，以后改菜单不影响历史订单。"""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"))
    name: Mapped[str] = mapped_column(String(128))
    price_cents: Mapped[int] = mapped_column(Integer)
    qty: Mapped[int] = mapped_column(Integer)

    order: Mapped["Order"] = relationship(back_populates="items")


class CartItem(Base):
    """用户购物车行。同一用户同一道菜只有一行，qty 累加。"""

    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("user_id", "dish_id", name="uk_cart_user_dish"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"))
    qty: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    user: Mapped["User"] = relationship(back_populates="cart_items")
    dish: Mapped["Dish"] = relationship(back_populates="cart_items")
