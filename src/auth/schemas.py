import uuid
from fastapi_users import schemas
from datetime import datetime


class UserRead(schemas.BaseUser[int]):
    id: int
    email: str
    registered_at: datetime


class UserCreate(schemas.BaseUserCreate):
    id: int
    email: str
    password: str