from pydantic import BaseModel


class UserBase(BaseModel):
    fullname: str 
    description: str
    username: str
    is_admin: bool

class UserOut(UserBase):
    id: int

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    fullname: str | None = None
    description: str | None = None
    username: str | None = None
    is_admin: bool | None = None
    password: str | None = None

class UserLogin(BaseModel):
    username: str
    password: str