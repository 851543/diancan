"""
认证接口：注册、登录。
完整 URL = prefix + 路径，例如 POST /auth/login

@router.post 相当于 Java：
  @PostMapping("/register")
  public TokenOut register(@RequestBody RegisterIn body)
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import LoginIn, RegisterIn, TokenOut
from app.security import create_access_token, hash_password, verify_password

logger = logging.getLogger("diancan")
# prefix="/auth"：这个文件里所有路径前面都加 /auth
# tags=["auth"]：在 /docs 里分组显示
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    """
    步骤：
      1. FastAPI 把 JSON body 解析成 RegisterIn（校验长度）
      2. Depends(get_db) 打开数据库
      3. 查用户名是否已存在
      4. 密码哈希后插入
      5. db.commit() 真正写入 MySQL（不 commit 等于没保存）
      6. 直接发 JWT，注册完就算已登录
    """
    logger.info("注册 username=%s", body.username)
    exists = db.query(User).filter(User.username == body.username).first()
    if exists:
        logger.warning("用户名已存在 username=%s", body.username)
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=body.username,
        hashed_password=hash_password(body.password),  # 绝不存明文
        role="customer",
    )
    db.add(user)  # 放进「待提交」列表，还没进库
    db.commit()  # 提交事务
    token = create_access_token(user.username, user.role)
    logger.info("注册成功 user=%s username=%s", user.id, user.username)
    return TokenOut(access_token=token, role=user.role, username=user.username)


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    """
    步骤：
      1. 按用户名查库
      2. verify_password 比对明文和哈希
      3. 通过才发 token
    """
    logger.info("登录 username=%s", body.username)
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        logger.warning("登录失败 username=%s", body.username)
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
        )
    token = create_access_token(user.username, user.role)
    logger.info("登录成功 user=%s username=%s role=%s", user.id, user.username, user.role)
    return TokenOut(access_token=token, role=user.role, username=user.username)
