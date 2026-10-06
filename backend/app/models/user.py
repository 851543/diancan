from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import utcnow


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "用户账号"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键")
    username: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, comment="登录用户名"
    )
    hashed_password: Mapped[str] = mapped_column(String(255), comment="密码哈希，不存明文")
    role: Mapped[str] = mapped_column(
        String(16), default="customer", comment="角色：customer 顾客 / admin 店员"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, comment="注册时间"
    )

    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    cart_items: Mapped[list["CartItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
