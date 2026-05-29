from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from services.storage import (
    UPLOADS_DIR,
    get_project_or_404,
    new_track_id,
    tracks,
)
from sessions.track_session import TrackSession


router = APIRouter()


@router.post("/projects/{project_id}/tracks", response_model=TrackSession)
async def upload_track(project_id: str, request: Request, file: UploadFile = File(...)) -> TrackSession:
    project = get_project_or_404(project_id)
    filename = (file.filename or "").strip()
    if not filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only WAV files are supported.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    track_id = new_track_id()
    safe_name = Path(filename).name
    saved_name = f"{track_id}_{safe_name}"
    saved_path = UPLOADS_DIR / saved_name
    saved_path.write_bytes(content)

    file_url = str(request.base_url).rstrip("/") + f"/files/uploads/{saved_name}"
    track = TrackSession(
        track_id=track_id,
        project_id=project_id,
        filename=safe_name,
        file_path=str(saved_path),
        file_url=file_url,
    )

    tracks[track_id] = track
    project.track_ids.append(track_id)
    return track


@router.get("/projects/{project_id}/tracks")
def list_tracks(project_id: str) -> list[dict]:
    get_project_or_404(project_id)
    return [track.model_dump() for track in tracks.values() if track.project_id == project_id]

