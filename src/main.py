import uvicorn
from fastapi import FastAPI
from src.auth.auth import auth_backend
from src.auth.schemas import UserRead, UserCreate
from src.auth.manager import fastapi_users
from src.links.routers import router as links_router
from src.auth.models import User  # noqa: F401
from src.links.models import Link  # noqa: F401
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(links_router)