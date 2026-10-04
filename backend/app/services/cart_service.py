"""
顾客端购物车：MySQL 表 cart_items 落库，Redis Hash 加速。
Java 对照：DB + RedisTemplate.opsForHash()
key = cart:{user_id}，field=dish_id，value=qty
"""

import logging

import redis
from sqlalchemy.orm import Session

from app.models import CartItem, Dish
from app.redis_client import redis_client

logger = logging.getLogger("diancan")


def _key(user_id: int) -> str:
    return f"cart:{user_id}"


def _from_hash(raw: dict) -> dict[str, int]:
    return {str(k): int(v) for k, v in (raw or {}).items() if int(v) > 0}


def _load_mysql_qty(db: Session, user_id: int) -> dict[str, int]:
    rows = (
        db.query(CartItem.dish_id, CartItem.qty)
        .filter(CartItem.user_id == user_id, CartItem.qty > 0)
        .all()
    )
    mapping = {str(dish_id): int(qty) for dish_id, qty in rows}
    logger.info("MySQL 读购物车数量 user=%s %s", user_id, mapping)
    return mapping


def _write_hash(user_id: int, mapping: dict[str, int]) -> None:
    key = _key(user_id)
    try:
        redis_client.delete(key)
        if mapping:
            redis_client.hset(key, mapping=mapping)
        logger.info("Redis Hash 写入 key=%s %s", key, mapping)
    except redis.RedisError as exc:
        logger.warning("Redis Hash 写入失败 key=%s err=%s", key, exc)


def get_cart(db: Session, user_id: int) -> dict[str, int]:
    key = _key(user_id)
    try:
        raw = redis_client.hgetall(key)
        mapping = _from_hash(raw)
        if mapping:
            logger.info("Redis Hash 命中 key=%s %s", key, mapping)
            return mapping
        logger.info("Redis Hash 未命中 key=%s", key)
    except redis.RedisError as exc:
        logger.warning("Redis Hash 读取失败 key=%s err=%s", key, exc)
    mapping = _load_mysql_qty(db, user_id)
    _write_hash(user_id, mapping)
    return mapping


def add_item(db: Session, user_id: int, dish_id: int, qty: int) -> list[dict]:
    logger.info("加购 MySQL+Redis user=%s dish=%s qty=%s", user_id, dish_id, qty)
    row = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id, CartItem.dish_id == dish_id)
        .first()
    )
    if row:
        row.qty += qty
        if row.qty <= 0:
            db.delete(row)
            logger.info("MySQL 删除购物车行 user=%s dish=%s", user_id, dish_id)
        else:
            logger.info("MySQL 更新数量 user=%s dish=%s qty=%s", user_id, dish_id, row.qty)
    elif qty > 0:
        db.add(CartItem(user_id=user_id, dish_id=dish_id, qty=qty))
        logger.info("MySQL 新增购物车行 user=%s dish=%s qty=%s", user_id, dish_id, qty)
    db.commit()
    mapping = _load_mysql_qty(db, user_id)
    _write_hash(user_id, mapping)
    return get_items(db, user_id)


def get_items(db: Session, user_id: int) -> list[dict]:
    mapping = get_cart(db, user_id)
    items: list[dict] = []
    for dish_id, qty in mapping.items():
        dish = db.query(Dish).filter(Dish.id == int(dish_id)).first()
        if not dish:
            continue
        items.append(
            {
                "dish_id": dish.id,
                "name": dish.name,
                "price_cents": dish.price_cents,
                "qty": qty,
            }
        )
    items.sort(key=lambda x: x["dish_id"])
    logger.info("购物车明细 user=%s 共 %s 条", user_id, len(items))
    return items


def clear_cart(db: Session, user_id: int) -> None:
    deleted = db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
    key = _key(user_id)
    try:
        redis_client.delete(key)
        logger.info("Redis 删除 Hash key=%s", key)
    except redis.RedisError as exc:
        logger.warning("Redis 删除失败 key=%s err=%s", key, exc)
    logger.info("清空购物车 user=%s MySQL删除 %s 行", user_id, deleted)
