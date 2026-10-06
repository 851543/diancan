"""程序入口：uvicorn app.main:app"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    force=True,
)
logger = logging.getLogger("diancan")

from app.core.config import settings
from app.db.redis import redis_client
from app.routers import auth, cart, dishes, orders

logging.getLogger("sqlalchemy.engine").setLevel(
    logging.WARNING if settings.is_production else logging.INFO
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.is_production and settings.jwt_secret in (
        "",
        "change-me-in-production",
        "change-me",
    ):
        raise RuntimeError("生产环境必须在 .env 中设置 JWT_SECRET")
    logger.info(
        "启动成功，MySQL %s@%s:%s/%s",
        settings.mysql_user,
        settings.mysql_host,
        settings.mysql_port,
        settings.mysql_db,
    )
    try:
        ok = redis_client.ping()
        logger.info("Redis ping=%s %s:%s", ok, settings.redis_host, settings.redis_port)
    except Exception as exc:
        logger.warning("Redis 未就绪: %s", exc)
    yield


app = FastAPI(
    title="点餐 API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    logger.info("请求 %s %s", request.method, request.url.path)
    response = await call_next(request)
    cost_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "响应 %s %s -> %s (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        cost_ms,
    )
    return response


app.include_router(auth.router)
app.include_router(dishes.router)
app.include_router(orders.router)
app.include_router(cart.router)


@app.get("/health")
def health():
    return {"ok": True}
