"""密码哈希 + JWT。"""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# passlib 1.7.4 会读 bcrypt.__about__，bcrypt 4.1+ 已去掉该属性
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("_About", (), {"__version__": bcrypt.__version__})()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(sub: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": sub, "role": role, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
