from pydantic import BaseModel, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class LoginIn(BaseModel):
    username: str
    password: str


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=64)
