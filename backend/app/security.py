"""
密码哈希 + JWT 签发/解析。
Java 对照：PasswordEncoder + JwtTokenProvider。
"""

# datetime：当前时间；timedelta：时间加减；timezone.utc：用 UTC，避免时区坑
from datetime import datetime, timedelta, timezone

# jose：JWT 库。jwt.encode 签发，jwt.decode 校验。JWTError 是校验失败抛的异常。
from jose import JWTError, jwt

# CryptContext：选一种哈希算法（这里 bcrypt）。类似 Spring 的 BCryptPasswordEncoder。
from passlib.context import CryptContext

from app.config import settings

# schemes=["bcrypt"]：只用 bcrypt 一种算法。
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """
    明文 -> 哈希。注册、seed 时调用。
    -> str 表示返回值是字符串。Java：public String hashPassword(String plain)
    """
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """
    用 passlib 校验明文密码和数据库里的哈希是否匹配。
    Java 对照：PasswordEncoder.matches(raw, encoded)

    完成后应返回 True/False，而不是永远 False。
    提示：return pwd_context.verify(plain, hashed)
    """
    return pwd_context.verify(plain, hashed)


def create_access_token(sub: str, role: str) -> str:
    """
    登录成功后发 JWT。
    sub = 用户名（subject），role = customer/admin。
    payload 会变成 token 里的 JSON 声明。
    """
    # 现在(UTC) + N 分钟 = 过期时间
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    # dict 类似 Java 的 Map<String, Object>
    payload = {"sub": sub, "role": role, "exp": expire}
    # 用密钥签名。别人没有 JWT_SECRET 就伪造不了。
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    """
    解析 token。成功返回 dict；失败返回 None（Python 的 null）。
    dict | None 意思：返回字典或空。Java：Map 或 null。
    """
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        # Java 对照：catch (JwtException e) { return null; }
        return None
