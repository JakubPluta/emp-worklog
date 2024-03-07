from pydantic import UUID4, BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True


class UserUpdate(UserBase):
    name: str | None = None
    email: str | None = None
    password: str | None = None
    is_superuser: bool | None = None
    is_active: bool | None = None


class UserUpdatePassowrd(BaseModel):
    password: str


class UserCreate(UserBase):
    email: EmailStr
    password: str
    is_superuser: bool = False


class UserInDB(UserBase):
    hashed_password: str
    is_superuser: bool = False


class UserOut(UserBase):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)


class UserUpdateSelf(BaseModel):
    name: str
    password: str | None = None
