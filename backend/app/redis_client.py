"""
Redis 客户端（全局一份）。
顾客端接口用它做缓存；商家后台接口不要直接调用。
"""

import redis

from app.config import settings

# decode_responses=True：读出来是 str，不是 bytes。
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True,
)
