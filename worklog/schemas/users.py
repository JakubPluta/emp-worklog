from pydantic import BaseModel, ConfigDict
from pydantic import EmailStr, UUID4

class UserBase(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True
    

class UserUpdate(UserBase):
    password: str
    is_superuser: bool = False


class UserCreate(UserBase):
    email: EmailStr
    password: str
    is_superuser: bool = False


class UserInDB(UserBase):
    id: str
    hashed_password: str


class UserOut(UserBase):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)
    
