"""
菜品接口。
顾客：GET /dishes（只看上架）
店员：GET/POST/PUT /dishes/admin（要 JWT 且 role=admin）
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import Dish, User
from app.schemas import DishIn, DishOut

logger = logging.getLogger("diancan")
router = APIRouter(prefix="/dishes", tags=["dishes"])


def _filter_dishes(query, keyword: str | None, category: str | None):
    if keyword:
        query = query.filter(Dish.name.like(f"%{keyword}%"))
    if category:
        query = query.filter(Dish.category == category)
    if not keyword and not category:
        query = query.filter(Dish.is_on == 1)
    return query


@router.get("", response_model=list[DishOut])
def list_dishes(
    keyword: str | None = None,  # 查询参数 ?keyword=蛋  没传就是 None
    category: str | None = None,  # ?category=热菜
    db: Session = Depends(get_db),
):
    """顾客菜单：只返回 is_on==1 的。"""
    logger.info("顾客查菜单 keyword=%s category=%s", keyword, category)
    q = db.query(Dish).filter(Dish.is_on == 1)
    q = _filter_dishes(q, keyword, category)
    dishes = q.order_by(Dish.id.asc()).all()
    logger.info("顾客查菜单结果 %s 条", len(dishes))
    return dishes


@router.get("/admin", response_model=list[DishOut])
def admin_list_dishes(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),  # 没登录或不是 admin，这里直接 401/403
):
    """店员看全部菜（含下架）。"""
    logger.info("店员查全部菜品")
    rows = db.query(Dish).order_by(Dish.id.asc()).all()
    logger.info("店员查全部菜品 共 %s 条", len(rows))
    return rows


@router.post("/admin", response_model=DishOut)
def create_dish(
    body: DishIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    body.model_dump()：DTO 转成普通 dict，例如 {"name": "米饭", ...}
    Dish(**dict)：把 dict 拆成关键字参数。Java 类似用构造器或 setter 填字段。
    db.refresh：提交后把数据库生成的 id 填回对象。
    """
    logger.info("新增菜品 %s", body.name)
    dish = Dish(**body.model_dump())
    db.add(dish)
    db.commit()
    db.refresh(dish)
    logger.info("新增菜品成功 id=%s", dish.id)
    return dish


@router.put("/admin/{dish_id}", response_model=DishOut)
def update_dish(
    dish_id: int,  # 路径参数 /dishes/admin/3 里的 3。Java：@PathVariable
    body: DishIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    logger.info("修改菜品 id=%s name=%s", dish_id, body.name)
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        logger.warning("菜品不存在 id=%s", dish_id)
        raise HTTPException(status_code=404, detail="菜品不存在")
    # items()：遍历 dict 的每个键值对。setattr(对象, 字段名, 值) 动态赋值。
    for k, v in body.model_dump().items():
        setattr(dish, k, v)
    db.commit()
    db.refresh(dish)
    logger.info("修改菜品成功 id=%s", dish.id)
    return dish
