from datetime import datetime

from pydantic import BaseModel, Field


class OrderItemIn(BaseModel):
    dish_id: int
    qty: int = Field(gt=0)


class OrderCreateIn(BaseModel):
    items: list[OrderItemIn] = []
    remark: str = ""


class OrderItemOut(BaseModel):
    dish_id: int
    name: str
    price_cents: int
    qty: int

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: int
    user_id: int
    username: str = ""
    status: str
    total_cents: int
    remark: str
    created_at: datetime
    items: list[OrderItemOut]

    model_config = {"from_attributes": True}


class StatusIn(BaseModel):
    status: str
