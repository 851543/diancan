"""订单：下单、查询、状态流转。"""

import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models import Dish, Order, OrderItem, User
from app.schemas import OrderCreateIn, OrderItemIn
from app.services.cart_service import clear_cart, get_items

logger = logging.getLogger("diancan")

ALLOWED_FROM = {
    "pending": {"paid", "cancelled"},
    "paid": {"preparing", "cancelled"},
    "preparing": {"ready", "cancelled"},
    "ready": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


def can_transition(current: str, target: str) -> bool:
    allowed = ALLOWED_FROM.get(current, set())
    ok = target in allowed
    logger.info("状态流转 %s -> %s 允许=%s", current, target, ok)
    return ok


def order_query(db: Session):
    return db.query(Order).options(joinedload(Order.items), joinedload(Order.user))


def create_order(db: Session, user: User, body: OrderCreateIn) -> Order:
    logger.info(
        "下单 user=%s username=%s 行数=%s",
        user.id,
        user.username,
        len(body.items),
    )
    lines = list(body.items)
    if not lines:
        lines = [
            OrderItemIn(dish_id=row["dish_id"], qty=row["qty"])
            for row in get_items(db, user.id)
        ]
    if not lines:
        logger.warning("购物车是空的 user=%s", user.id)
        raise HTTPException(status_code=400, detail="购物车是空的")
    order = Order(user_id=user.id, status="pending", remark=body.remark)
    total = 0
    for line in lines:
        dish = db.query(Dish).filter(Dish.id == line.dish_id, Dish.is_on == 1).first()
        if not dish:
            logger.warning("下单失败 菜品不可点 user=%s dish=%s", user.id, line.dish_id)
            raise HTTPException(status_code=400, detail=f"菜品不可点: {line.dish_id}")
        order.items.append(
            OrderItem(
                dish_id=dish.id,
                name=dish.name,
                price_cents=dish.price_cents,
                qty=line.qty,
            )
        )
        total += dish.price_cents * line.qty
    order.total_cents = total
    db.add(order)
    db.commit()
    order = order_query(db).filter(Order.id == order.id).first()
    logger.info("下单成功 order=%s user=%s total_cents=%s", order.id, user.id, order.total_cents)
    try:
        clear_cart(db, user.id)
        logger.info("下单后已清空购物车 user=%s", user.id)
    except Exception:
        logger.exception("下单成功但清空购物车失败 user=%s", user.id)
    return order


def list_mine(db: Session, user_id: int) -> list[Order]:
    return (
        order_query(db)
        .filter(Order.user_id == user_id)
        .order_by(Order.id.desc())
        .unique()
        .all()
    )


def list_admin(db: Session, status: str | None = None) -> list[Order]:
    q = order_query(db)
    if status:
        q = q.filter(Order.status == status)
    return q.order_by(Order.id.desc()).unique().all()


def change_status(db: Session, order: Order, target: str) -> Order:
    if not can_transition(order.status, target):
        logger.warning("非法流转 order=%s %s -> %s", order.id, order.status, target)
        raise HTTPException(
            status_code=400,
            detail=f"不能从 {order.status} 改到 {target}",
        )
    old = order.status
    order.status = target
    db.commit()
    order = order_query(db).filter(Order.id == order.id).first()
    logger.info("改订单状态成功 order=%s %s -> %s", order.id, old, order.status)
    return order
