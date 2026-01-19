from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(..., example="Alice")
    email: str = Field(..., example="alice@example.com")
    phone: str = Field(..., example="+1234567890")
    password: str = Field(..., example="strongpassword")

    class Config:
        json_schema_extra = {
            "example": {"name": "Alice", "email": "alice@example.com", "phone": "+1234567890", "password": "strongpassword"}
        }


class UserLogin(BaseModel):
    email: str = Field(..., example="alice@example.com")
    password: str = Field(..., example="strongpassword")

    class Config:
        json_schema_extra = {
            "example": {"email": "alice@example.com", "password": "strongpassword"}
        }
