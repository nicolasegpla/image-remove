from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict
from uuid import UUID
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    code_auth: str
    country: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID  
    email: EmailStr
    id_api: str
    status: bool
    tokens: int
    type_user: str
    country: str | None

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    country: Optional[str] = None
    status: Optional[bool] = None
    tokens: Optional[int] = None
    type_user: Optional[str] = None
    code_auth: Optional[str] = None