"""菜品查询与维护。"""

import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import CartItem, Dish, OrderItem
from app.schemas import DishIn

logger = logging.getLogger("diancan")


def filter_query(query, keyword: str | None, category: str | None):
    if keyword:
        query = query.filter(Dish.name.like(f"%{keyword}%"))
    if category:
        query = query.filter(Dish.category == category)
    if not keyword and not category:
        query = query.filter(Dish.is_on == 1)
    return query


def list_on_sale(db: Session, keyword: str | None, category: str | None) -> list[Dish]:
    q = db.query(Dish).filter(Dish.is_on == 1)
    q = filter_query(q, keyword, category)
    return q.order_by(Dish.id.asc()).all()


def list_all(db: Session) -> list[Dish]:
    return db.query(Dish).order_by(Dish.id.asc()).all()


def create(db: Session, body: DishIn) -> Dish:
    dish = Dish(**body.model_dump())
    db.add(dish)
    db.commit()
    db.refresh(dish)
    return dish


def update(db: Session, dish_id: int, body: DishIn) -> Dish:
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")
    for k, v in body.model_dump().items():
        setattr(dish, k, v)
    db.commit()
    db.refresh(dish)
    return dish


def delete(db: Session, dish_id: int) -> None:
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")
    used = db.query(OrderItem).filter(OrderItem.dish_id == dish_id).first()
    if used:
        raise HTTPException(status_code=400, detail="已有订单包含该菜，只能下架")
    db.query(CartItem).filter(CartItem.dish_id == dish_id).delete()
    db.delete(dish)
    db.commit()
