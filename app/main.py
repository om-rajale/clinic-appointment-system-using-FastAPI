from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import auth, users, doctors, appointments, records
from app.utils.reminders import start_scheduler

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


# ── Lifespan: start/stop background scheduler ─────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    yield
    scheduler.shutdown(wait=False)


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    description="REST API for clinic appointment scheduling with JWT authentication.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "null",  # file:// pages during local development
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(records.router)


# ── Health check ───────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "app": settings.app_name}


if FRONTEND_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(FRONTEND_DIR / "index.html")
else:

    @app.get("/", tags=["Health"])
    def root():
        return {"status": "ok", "app": settings.app_name}
