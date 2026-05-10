from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.auth import auth_backend
from src.database import get_db
from src.auth.models import User

from src.config import SECRET


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET


async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
current_optional_user = fastapi_users.current_user(optional=True)
current_user = fastapi_users.current_user()