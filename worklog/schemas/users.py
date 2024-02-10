from pydantic import UUID4, BaseModel, ConfigDict, EmailStr


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
    id: UUID4
    hashed_password: str


class UserOut(UserBase):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)
