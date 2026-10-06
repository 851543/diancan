"""订单接口。"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models import Order, User
from app.schemas import OrderCreateIn, OrderOut, StatusIn
from app.services import order_service

logger = logging.getLogger("diancan")
router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut)
def create_order(
    body: OrderCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return order_service.create_order(db, user, body)


@router.get("/me", response_model=list[OrderOut])
def my_orders(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info("查我的订单 user=%s", user.id)
    rows = order_service.list_mine(db, user.id)
    logger.info("查我的订单结果 user=%s 共 %s 条", user.id, len(rows))
    return rows


@router.patch("/me/{order_id}", response_model=OrderOut)
def change_my_order(
    order_id: int,
    body: StatusIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if body.status not in ("paid", "cancelled"):
        raise HTTPException(status_code=400, detail="只能支付或取消")
    logger.info("顾客改订单 order=%s user=%s -> %s", order_id, user.id, body.status)
    order = (
        order_service.order_query(db)
        .filter(Order.id == order_id, Order.user_id == user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order_service.change_status(db, order, body.status)


@router.get("/admin", response_model=list[OrderOut])
def admin_orders(
    status: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    logger.info("店员查全部订单 status=%s", status)
    rows = order_service.list_admin(db, status)
    logger.info("店员查全部订单 共 %s 条", len(rows))
    return rows


@router.patch("/admin/{order_id}", response_model=OrderOut)
def change_status(
    order_id: int,
    body: StatusIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    logger.info("改订单状态 order=%s -> %s", order_id, body.status)
    order = order_service.order_query(db).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order_service.change_status(db, order, body.status)
