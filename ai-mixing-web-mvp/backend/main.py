from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers.actions import router as actions_router
from routers.analysis import router as analysis_router
from routers.projects import router as projects_router
from routers.tracks import router as tracks_router


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="AI Mixing Assistant Web MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router, prefix="/api", tags=["projects"])
app.include_router(tracks_router, prefix="/api", tags=["tracks"])
app.include_router(analysis_router, prefix="/api", tags=["analysis"])
app.include_router(actions_router, prefix="/api", tags=["actions"])

app.mount("/files/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.mount("/files/processed", StaticFiles(directory=PROCESSED_DIR), name="processed")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

