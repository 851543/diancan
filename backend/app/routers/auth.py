"""认证：注册、登录。"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import User
from app.schemas import LoginIn, RegisterIn, TokenOut

logger = logging.getLogger("diancan")
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    logger.info("注册 username=%s", body.username)
    exists = db.query(User).filter(User.username == body.username).first()
    if exists:
        logger.warning("用户名已存在 username=%s", body.username)
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=body.username,
        hashed_password=hash_password(body.password),
        role="customer",
    )
    db.add(user)
    db.commit()
    token = create_access_token(user.username, user.role)
    logger.info("注册成功 user=%s username=%s", user.id, user.username)
    return TokenOut(access_token=token, role=user.role, username=user.username)


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    logger.info("登录 username=%s", body.username)
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        logger.warning("登录失败 username=%s", body.username)
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    token = create_access_token(user.username, user.role)
    logger.info("登录成功 user=%s username=%s role=%s", user.id, user.username, user.role)
    return TokenOut(access_token=token, role=user.role, username=user.username)
