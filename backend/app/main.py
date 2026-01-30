import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from .api.router import api_router
from .core.config import get_settings
from .database import Base, DATABASE_URL, engine

settings = get_settings()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_default],
)

app = FastAPI(title="Personal Life Dashboard MVP", version="0.1.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False if "*" in settings.cors_origins else True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    if DATABASE_URL.startswith("sqlite"):
        path = DATABASE_URL.replace("sqlite:///", "")
        data_dir = os.path.dirname(path)
        if data_dir:
            os.makedirs(data_dir, exist_ok=True)
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "ok"}

app.include_router(api_router)
