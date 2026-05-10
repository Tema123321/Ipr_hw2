from src.config import DATABASE_URL
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

Base = declarative_base()

# Асинхронный движок
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30
)

# Фабрика сессий
async_session = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False
)


# Dependency для FastAPI
async def get_db() -> AsyncSession:
    """Генератор сессий для Dependency Injection"""
    async with async_session() as session:
        yield session
