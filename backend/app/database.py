"""
数据库引擎和 Session。
Java 对照：DataSource + EntityManager / SessionFactory。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# 1) 创建引擎 = 连接池。pool_pre_ping=True：拿连接前先 ping，避免 MySQL 超时断线。
engine = create_engine(settings.database_url, pool_pre_ping=True)

# 2) Session 工厂。每次调用 SessionLocal() 得到一次「数据库会话」。
#    autoflush=False / autocommit=False：改了对象不会偷偷提交，要你自己 db.commit()。
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """
    所有实体类（User、Dish...）都继承它。
    Java 对照：所有 @Entity 的共同基类；Alembic 靠 Base.metadata 知道有哪些表。
    """

    pass


def get_db():
    """
    FastAPI 依赖注入：每个请求打开一个 Session，用完关闭。
    Java 对照：Filter 里获取 EntityManager，finally 里 close。

    yield 的意思：
      - 先执行到 yield，把 db 交给接口函数
      - 接口跑完后，继续执行 finally，关闭连接
    即使接口抛异常，也会 close。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
