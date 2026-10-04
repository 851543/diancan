"""
订单接口。
顾客：POST /orders 下单，GET /orders/me 我的订单
店员：GET /orders/admin 全部，PATCH /orders/admin/{id} 改状态
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_admin
from app.models import Dish, Order, OrderItem, User
from app.schemas import OrderCreateIn, OrderOut, StatusIn
from app.services import cart_service
from app.services.order_service import can_transition

logger = logging.getLogger("diancan")
router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut)
def create_order(
    body: OrderCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),  # 必须带 JWT，user 就是当前登录顾客
):
    """
    下单步骤：
      1. 购物车不能为空
      2. 新建一张订单（先 pending）
      3. 循环每一道菜：校验上架，拷贝当时价格进明细
      4. 累加总价（分）
      5. commit 一次写入订单+明细（因为配置了 cascade）
    """
    logger.info(
        "下单 user=%s username=%s 行数=%s",
        user.id,
        user.username,
        len(body.items),
    )
    if not body.items:
        logger.warning("购物车是空的 user=%s", user.id)
        raise HTTPException(status_code=400, detail="购物车是空的")
    order = Order(user_id=user.id, status="pending", remark=body.remark)
    total = 0
    for line in body.items:  # 类似 Java for (OrderItemIn line : body.getItems())
        dish = db.query(Dish).filter(Dish.id == line.dish_id, Dish.is_on == 1).first()
        if not dish:
            logger.warning("下单失败 菜品不可点 user=%s dish=%s", user.id, line.dish_id)
            raise HTTPException(status_code=400, detail=f"菜品不可点: {line.dish_id}")
        order.items.append(
            OrderItem(
                dish_id=dish.id,
                name=dish.name,
                price_cents=dish.price_cents,  # 锁价
                qty=line.qty,
            )
        )
        total += dish.price_cents * line.qty
    order.total_cents = total
    db.add(order)
    db.commit()
    db.refresh(order)
    logger.info("下单成功 order=%s user=%s total_cents=%s", order.id, user.id, order.total_cents)
    try:
        cart_service.clear_cart(db, user.id)
        logger.info("下单后已清空购物车 user=%s", user.id)
    except Exception:
        logger.exception("下单成功但清空购物车失败 user=%s", user.id)
    return order


@router.get("/me", response_model=list[OrderOut])
def my_orders(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """只查当前用户的订单，新的在前。"""
    logger.info("查我的订单 user=%s", user.id)
    rows = (
        db.query(Order)
        .filter(Order.user_id == user.id)
        .order_by(Order.id.desc())
        .all()
    )
    logger.info("查我的订单结果 user=%s 共 %s 条", user.id, len(rows))
    return rows


@router.get("/admin", response_model=list[OrderOut])
def admin_orders(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    logger.info("店员查全部订单")
    rows = db.query(Order).order_by(Order.id.desc()).all()
    logger.info("店员查全部订单 共 %s 条", len(rows))
    return rows


@router.patch("/admin/{order_id}", response_model=OrderOut)
def change_status(
    order_id: int,
    body: StatusIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    PATCH = 部分更新（这里只改 status）。
    非法状态跳转会 400。
    """
    logger.info("改订单状态 order=%s -> %s", order_id, body.status)
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        logger.warning("订单不存在 id=%s", order_id)
        raise HTTPException(status_code=404, detail="订单不存在")
    if not can_transition(order.status, body.status):
        logger.warning("非法流转 order=%s %s -> %s", order.id, order.status, body.status)
        raise HTTPException(
            status_code=400,
            detail=f"不能从 {order.status} 改到 {body.status}",
        )
    old = order.status
    order.status = body.status
    db.commit()
    db.refresh(order)
    logger.info("改订单状态成功 order=%s %s -> %s", order.id, old, order.status)
    return order
