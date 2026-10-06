"""
创建首个店员账号。不写入演示顾客、演示菜单。

在项目根目录 .env 配置：
  ADMIN_USERNAME=店员用户名
  ADMIN_PASSWORD=店员密码

运行（backend 目录、diancan 环境）：
  python -m app.seed
"""

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import User

def run() -> None:
    username = (settings.admin_username or "").strip()
    password = settings.admin_password or ""
    if not username or not password:
        print("未配置 ADMIN_USERNAME / ADMIN_PASSWORD，已跳过")
        return
    if len(username) < 3 or len(password) < 6:
        raise SystemExit("ADMIN_USERNAME 至少 3 位，ADMIN_PASSWORD 至少 6 位")

    db = SessionLocal()
    try:
        if db.query(User).filter(User.role == "admin").first():
            print("已有店员账号，跳过")
            return
        if db.query(User).filter(User.username == username).first():
            raise SystemExit(f"用户名已存在：{username}")
        db.add(
            User(
                username=username,
                hashed_password=hash_password(password),
                role="admin",
            )
        )
        db.commit()
        print(f"已创建店员账号：{username}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
