"""
依赖注入：从请求头取出 JWT，查出当前用户。
Java 对照：HandlerInterceptor / SecurityContextHolder.getContext().getAuthentication()

FastAPI 的 Depends(xxx)：
  调用接口前先执行 xxx，把返回值当参数传进来。
  类似 Spring 的参数解析器。
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_token

# 告诉 FastAPI：token 在 Header「Authorization: Bearer xxx」
# tokenUrl 只是给 /docs 的「Authorize」按钮用的路径提示。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),  # 1) 先从 Header 抽出 token
    db: Session = Depends(get_db),  # 2) 再打开数据库会话
) -> User:
    """任何需要「已登录」的接口，参数里写 user=Depends(get_current_user)。"""
    payload = decode_token(token)
    # not payload：None 或空。 "sub" not in payload：token 里没有用户名。
    if not payload or "sub" not in payload:
        # raise = Java 的 throw。HTTPException 会被 FastAPI 变成 HTTP 错误 JSON。
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效登录")
    # db.query(User).filter(...).first() 类似：
    #   SELECT * FROM users WHERE username = ? LIMIT 1
    user = db.query(User).filter(User.username == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """
    店员接口用这个。它内部会先走 get_current_user，再检查 role。
    参数名写成 _ 表示「我只要这个检查，函数体里不用这个变量」。
    """
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要店员权限")
    return user
