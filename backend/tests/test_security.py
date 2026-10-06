"""verify_password / hash_password 单元测试。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password, verify_password

# 完整 bcrypt 形如 $2b$12$ + 盐 + 摘要。你给的串少了开头的 $2b。
KNOWN_HASH = "$2b$12$tyDozfVR.rAPZqAhBsJ4iezpFCQXfy4YfAHRBL0i29qb033oJopeW"


def test_hash_then_verify_ok():
    hashed = hash_password("plain-secret")
    assert verify_password("plain-secret", hashed) is True


def test_wrong_password_is_false():
    hashed = hash_password("plain-secret")
    assert verify_password("other", hashed) is False


def test_known_hash_matches_user123():
    assert verify_password("user123", KNOWN_HASH) is True


def test_known_hash_rejects_admin123():
    assert verify_password("admin123", KNOWN_HASH) is False


if __name__ == "__main__":
    print("user123 ->", verify_password("user123", KNOWN_HASH))
    print("admin123 ->", verify_password("admin123", KNOWN_HASH))
