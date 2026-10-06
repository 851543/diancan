"""菜品接口。"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.db.session import get_db
from app.models import User
from app.schemas import DishIn, DishOut
from app.services import dish_service

logger = logging.getLogger("diancan")
router = APIRouter(prefix="/dishes", tags=["dishes"])


@router.get("", response_model=list[DishOut])
def list_dishes(
    keyword: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
):
    logger.info("顾客查菜单 keyword=%s category=%s", keyword, category)
    dishes = dish_service.list_on_sale(db, keyword, category)
    logger.info("顾客查菜单结果 %s 条", len(dishes))
    return dishes


@router.get("/admin", response_model=list[DishOut])
def admin_list_dishes(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    logger.info("店员查全部菜品")
    rows = dish_service.list_all(db)
    logger.info("店员查全部菜品 共 %s 条", len(rows))
    return rows


@router.post("/admin", response_model=DishOut)
def create_dish(
    body: DishIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    logger.info("新增菜品 %s", body.name)
    dish = dish_service.create(db, body)
    logger.info("新增菜品成功 id=%s", dish.id)
    return dish


@router.put("/admin/{dish_id}", response_model=DishOut)
def update_dish(
    dish_id: int,
    body: DishIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    logger.info("修改菜品 id=%s name=%s", dish_id, body.name)
    dish = dish_service.update(db, dish_id, body)
    logger.info("修改菜品成功 id=%s", dish.id)
    return dish


@router.delete("/admin/{dish_id}")
def delete_dish(
    dish_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    dish_service.delete(db, dish_id)
    logger.info("删除菜品成功 id=%s", dish_id)
    return {"ok": True}
