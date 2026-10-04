"""
程序入口：创建 FastAPI 应用、挂中间件、挂路由。
启动命令：uvicorn app.main:app
  - app.main = 这个文件
  - :app    = 下面这个变量名

Java 对照：SpringBootApplication 主类 + @RequestMapping 扫包。
请求进来的顺序：CORS 中间件 -> 匹配路由 -> 执行函数 -> 返回 JSON。

python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# 先配日志，再 import 其它模块，这样连库、SQL 也会打出来。
# Java 对照：logback / logging.level.root=INFO
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    force=True,  # uvicorn 可能已经配过日志，强制覆盖，保证能看到
)
logger = logging.getLogger("diancan")
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)  # 打印实际 SQL

from app.config import settings
from app.redis_client import redis_client
from app.routers import auth, cart, dishes, orders


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # 启动时打一行，方便确认连的是哪个库（不打印密码）
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


# 1) 创建应用对象。title/version 会出现在 /docs 页面顶部。
app = FastAPI(title="点餐 API", version="0.1.0", lifespan=lifespan)

# 2) 跨域：浏览器从 5173（后台）或 H5 访问 8000 时，需要允许。
#    Java 对照：CorsFilter / WebMvcConfigurer.addCorsMappings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发期允许任意前端域名；上线要改成具体地址
    allow_credentials=False,
    allow_methods=["*"],  # GET/POST/PUT/PATCH/DELETE 都放行
    allow_headers=["*"],  # 允许 Authorization 等请求头
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """每个请求进出都打日志。Java 对照：HandlerInterceptor / Filter。"""
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


# 3) 顾客端购物车走 Redis Hash + MySQL；商家 /admin 只走 MySQL。
app.include_router(auth.router)  # /auth/login, /auth/register
app.include_router(dishes.router)  # /dishes ...
app.include_router(orders.router)  # /orders ...
app.include_router(cart.router)  # /cart ...


@app.get("/health")
def health():
    """
    探活接口：用来确认进程活着。
    Java 对照：@GetMapping("/health") 返回 Map。
    Python 直接 return dict，FastAPI 会自动变成 JSON。
    """
    return {"ok": True}
