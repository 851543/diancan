"""
请求/响应的 JSON 形状（DTO）。
和 models.py 分开：表结构 ≠ 接口暴露的字段（密码哈希不能返回给前端）。

Java 对照：LoginRequest / OrderVO。
Pydantic 会自动：
  - 校验类型（qty 必须是 int）
  - 校验范围（Field(gt=0) 表示必须 > 0）
  - 把 JSON <-> 对象互转
"""

from datetime import datetime

from pydantic import BaseModel, Field


class TokenOut(BaseModel):
    """登录/注册成功后返回给前端的内容。"""

    access_token: str
    token_type: str = "bearer"  # 前端拼 Header：Bearer <token>
    role: str
    username: str


class LoginIn(BaseModel):
    username: str
    password: str


class RegisterIn(BaseModel):
    # Field 用来加约束。Java：@Size(min=3, max=64)
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=64)


class DishOut(BaseModel):
    id: int
    name: str
    category: str
    description: str
    price_cents: int
    image_url: str
    is_on: int

    # from_attributes=True：允许从 SQLAlchemy 实体 Dish 直接转成这个 DTO。
    # Java 对照：BeanUtils.copyProperties 或 MapStruct。
    model_config = {"from_attributes": True}


class DishIn(BaseModel):
    """新增/编辑菜品时，前端传来的 JSON。"""

    name: str
    category: str
    description: str = ""
    price_cents: int = Field(gt=0)  # 必须大于 0 分
    image_url: str = ""
    is_on: int = 1


class OrderItemIn(BaseModel):
    dish_id: int
    qty: int = Field(gt=0)


class OrderCreateIn(BaseModel):
    items: list[OrderItemIn]  # JSON 数组。Java：List<OrderItemIn>
    remark: str = ""


class OrderItemOut(BaseModel):
    dish_id: int
    name: str
    price_cents: int
    qty: int

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: int
    status: str
    total_cents: int
    remark: str
    created_at: datetime
    items: list[OrderItemOut]

    model_config = {"from_attributes": True}


class StatusIn(BaseModel):
    """改订单状态：{"status": "paid"}"""

    status: str
