from pydantic import BaseModel, Field


class DishOut(BaseModel):
    id: int
    name: str
    category: str
    description: str
    price_cents: int
    image_url: str
    is_on: int

    model_config = {"from_attributes": True}


class DishIn(BaseModel):
    name: str
    category: str
    description: str = ""
    price_cents: int = Field(gt=0)
    image_url: str = ""
    is_on: int = 1
