"""
订单状态机。合法流转请你补全。

set() 是空集合。{"paid", "cancelled"} 是集合，里面的值不重复、无序。
Java 对照：Map<String, Set<String>>
"""

import logging

logger = logging.getLogger("diancan")

ALLOWED_FROM = {
    "pending": {"paid", "cancelled"},
    "paid": {"preparing", "cancelled"},
    "preparing": {"ready", "cancelled"},
    "ready": {"completed", "cancelled"},
    "completed": set(),  # 空：不能再改
    "cancelled": set(),
}


def can_transition(current: str, target: str) -> bool:
    """根据 ALLOWED_FROM 判断 current -> target 是否合法。"""
    allowed = ALLOWED_FROM.get(current, set())
    ok = target in allowed
    logger.info("状态流转 %s -> %s 允许=%s", current, target, ok)
    return ok
