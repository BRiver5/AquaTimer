from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import Base, engine
from .routers import intake, reminders, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AquaTimer API",
    description=(
        "Reference FastAPI + SQLAlchemy + SQLite backend for AquaTimer, mirroring the "
        "on-device SQLite schema the shipped mobile app uses by default. Not required "
        "at runtime by the app (which is local-first) — provided for parity/future sync."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(intake.router)
app.include_router(reminders.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
