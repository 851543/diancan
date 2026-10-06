from pydantic import BaseModel, Field


class CartItemIn(BaseModel):
    dish_id: int
    qty: int = Field(..., description="增量，加购传 1，减数量传 -1")


class CartLineOut(BaseModel):
    dish_id: int
    name: str
    price_cents: int
    qty: int


class CartOut(BaseModel):
    items: list[CartLineOut]
