from pydantic import BaseModel, ConfigDict
from pydantic import EmailStr

class BaseUser(BaseModel):
    pass
    

class UserUpdate(BaseUser):
    password: str


class UserCreate(BaseUser):
    email: EmailStr
    password: str