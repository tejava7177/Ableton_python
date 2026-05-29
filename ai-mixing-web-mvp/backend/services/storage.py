from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException

from sessions.action_session import ActionSession
from sessions.analysis_session import AnalysisSession
from sessions.project_session import ProjectSession
from sessions.track_session import TrackSession


BASE_DIR = Path(__file__).resolve().parents[1]
UPLOADS_DIR = BASE_DIR / "data" / "uploads"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

projects: dict[str, ProjectSession] = {}
tracks: dict[str, TrackSession] = {}
analyses: dict[str, AnalysisSession] = {}
actions: dict[str, ActionSession] = {}


def new_project_id() -> str:
    return f"proj_{uuid4().hex[:10]}"


def new_track_id() -> str:
    return f"track_{uuid4().hex[:10]}"


def new_analysis_id() -> str:
    return f"analysis_{uuid4().hex[:10]}"


def new_action_id() -> str:
    return f"action_{uuid4().hex[:10]}"


def get_project_or_404(project_id: str) -> ProjectSession:
    project = projects.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
    return project


def get_track_or_404(track_id: str) -> TrackSession:
    track = tracks.get(track_id)
    if track is None:
        raise HTTPException(status_code=404, detail=f"Track not found: {track_id}")
    return track


def get_analysis_for_track(track_id: str) -> AnalysisSession | None:
    for analysis in analyses.values():
        if analysis.track_id == track_id:
            return analysis
    return None


def get_actions_for_track(track_id: str) -> list[ActionSession]:
    return [action for action in actions.values() if action.track_id == track_id]

