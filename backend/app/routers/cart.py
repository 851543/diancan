"""
购物车接口（顾客端）：MySQL 落库 + Redis Hash。
GET/POST/DELETE /cart 需要登录。
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Dish, User
from app.services import cart_service

logger = logging.getLogger("diancan")
router = APIRouter(prefix="/cart", tags=["cart"])


class CartItemIn(BaseModel):
    dish_id: int
    qty: int = Field(..., description="增量，加购传 1，减数量传 -1")


class CartLineOut(BaseModel):
    dish_id: int
    name: str
    price_cents: int
    qty: int


class CartOut(BaseModel):
    items: list[CartLineOut]


def _to_out(items: list[dict]) -> CartOut:
    return CartOut(
        items=[
            CartLineOut(
                dish_id=row["dish_id"],
                name=row["name"],
                price_cents=row["price_cents"],
                qty=row["qty"],
            )
            for row in items
        ]
    )


@router.get("", response_model=CartOut)
def get_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info("查购物车 user=%s username=%s", user.id, user.username)
    out = _to_out(cart_service.get_items(db, user.id))
    logger.info("查购物车结果 user=%s 共 %s 条", user.id, len(out.items))
    return out


@router.post("", response_model=CartOut)
def add_cart(
    body: CartItemIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(
        "改购物车 user=%s username=%s dish=%s qty=%s",
        user.id,
        user.username,
        body.dish_id,
        body.qty,
    )
    if body.qty == 0:
        logger.warning("qty 为 0 user=%s", user.id)
        raise HTTPException(status_code=400, detail="qty 不能为 0")
    if body.qty > 0:
        dish = db.query(Dish).filter(Dish.id == body.dish_id, Dish.is_on == 1).first()
        if not dish:
            logger.warning("菜品不可点 user=%s dish=%s", user.id, body.dish_id)
            raise HTTPException(status_code=400, detail="菜品不可点")
    out = _to_out(cart_service.add_item(db, user.id, body.dish_id, body.qty))
    logger.info("改购物车成功 user=%s 共 %s 条", user.id, len(out.items))
    return out


@router.delete("")
def clear(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info("清空购物车 user=%s username=%s", user.id, user.username)
    cart_service.clear_cart(db, user.id)
    logger.info("清空购物车成功 user=%s", user.id)
    return {"ok": True}
