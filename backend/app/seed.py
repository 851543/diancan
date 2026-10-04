"""
初始化演示账号和菜单。可重复执行：已存在就跳过，不会重复插入。

运行方式（在 backend 目录、diancan 环境）：
  python -m app.seed
"""

from app.database import SessionLocal
from app.models import User
from app.security import hash_password


def run() -> None:
    db = SessionLocal()
    try:
        # .first() 没有就是 None，if not xxx 就为真。
        if not db.query(User).filter(User.username == "admin").first():
            db.add(
                User(
                    username="admin",
                    hashed_password=hash_password("admin123"),
                    role="admin",
                )
            )
        if not db.query(User).filter(User.username == "user").first():
            db.add(
                User(
                    username="user",
                    hashed_password=hash_password("user123"),
                    role="customer",
                )
            )
        db.commit()
    finally:
        # 无论成功失败都关闭连接。Java：try-with-resources / finally close
        db.close()


# 只有「直接运行这个文件」时才进这里。被别人 import 时不会自动灌数据。
# Java 对照：public static void main
if __name__ == "__main__":
    run()
