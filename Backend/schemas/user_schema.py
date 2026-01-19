from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str = Field(..., example="alice@example.com")
    password: str = Field(..., example="strongpassword")

    class Config:
        json_schema_extra = {
            "example": {"email": "alice@example.com", "password": "strongpassword"}
        }


class UserLogin(BaseModel):
    email: str = Field(..., example="alice@example.com")
    password: str = Field(..., example="strongpassword")

    class Config:
        json_schema_extra = {
            "example": {"email": "alice@example.com", "password": "strongpassword"}
        }
