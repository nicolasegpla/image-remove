from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from pydantic import ConfigDict
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    country: Optional[str] = None

class UserCreate(UserBase):
    password: str
    code_auth: str  # código que se valida en el registro

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: UUID  # Assuming UUID is imported from uuid
    id_api: str
    status: bool
    tokens: int
    type_user: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
