from uuid import UUID

from pydantic import BaseModel, EmailStr


from app.schemas.enums.enums import UserRole


class UserBase(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(UserBase):
    id: UUID
    role: UserRole
    is_active: bool
