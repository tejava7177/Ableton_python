from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from services.audio_processing import apply_low_high_cut
from services.storage import (
    PROCESSED_DIR,
    actions,
    get_project_or_404,
    get_track_or_404,
    new_action_id,
)
from sessions.action_session import ActionSession


router = APIRouter()


class LowHighCutRequest(BaseModel):
    low_cut_hz: float
    high_cut_hz: float


class UpdateActionStatusRequest(BaseModel):
    status: str


@router.post("/tracks/{track_id}/actions/low-high-cut", response_model=ActionSession)
def low_high_cut(track_id: str, payload: LowHighCutRequest, request: Request) -> ActionSession:
    track = get_track_or_404(track_id)
    project = get_project_or_404(track.project_id)

    if payload.low_cut_hz < 20.0 or payload.low_cut_hz > 1000.0:
        raise HTTPException(status_code=400, detail="Low Cut must be between 20Hz and 1000Hz.")
    if payload.high_cut_hz < 1000.0 or payload.high_cut_hz > 22000.0:
        raise HTTPException(status_code=400, detail="High Cut must be between 1000Hz and 22000Hz.")
    if payload.low_cut_hz >= payload.high_cut_hz:
        raise HTTPException(status_code=400, detail="Low Cut must be lower than High Cut.")

    action_id = new_action_id()
    output_name = f"{action_id}_{Path(track.filename).stem}_low_high_cut.wav"
    output_path = PROCESSED_DIR / output_name
    apply_low_high_cut(track.file_path, output_path, payload.low_cut_hz, payload.high_cut_hz)

    processed_file_url = str(request.base_url).rstrip("/") + f"/files/processed/{output_name}"
    action = ActionSession(
        action_id=action_id,
        track_id=track_id,
        type="low_high_cut",
        status="completed",
        params=payload.model_dump(),
        processed_file_url=processed_file_url,
    )

    actions[action_id] = action
    project.action_ids.append(action_id)
    track.status = "processed"
    return action


@router.get("/tracks/{track_id}/actions")
def list_track_actions(track_id: str) -> list[dict]:
    get_track_or_404(track_id)
    return [action.model_dump() for action in actions.values() if action.track_id == track_id]


@router.patch("/actions/{action_id}", response_model=ActionSession)
def update_action_status(action_id: str, payload: UpdateActionStatusRequest) -> ActionSession:
    action = actions.get(action_id)
    if action is None:
        raise HTTPException(status_code=404, detail=f"Action not found: {action_id}")

    normalized_status = payload.status.strip().lower()
    if normalized_status not in {"pending", "completed", "approved", "cancelled"}:
        raise HTTPException(status_code=400, detail="Unsupported action status.")

    action.status = normalized_status
    return action
