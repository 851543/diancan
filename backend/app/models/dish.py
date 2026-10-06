from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Dish(Base):
    __tablename__ = "dishes"
    __table_args__ = {"comment": "菜品菜单"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键")
    name: Mapped[str] = mapped_column(String(128), comment="菜名")
    category: Mapped[str] = mapped_column(String(64), index=True, comment="分类，如热菜/素菜")
    description: Mapped[str] = mapped_column(Text, default="", comment="简介")
    price_cents: Mapped[int] = mapped_column(Integer, comment="单价，单位分")
    image_url: Mapped[str] = mapped_column(String(512), default="", comment="图片地址")
    is_on: Mapped[int] = mapped_column(Integer, default=1, comment="是否上架：1 上架，0 下架")
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="dish")
