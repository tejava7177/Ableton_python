from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter

from services.storage import (
    analyses,
    get_project_or_404,
    get_actions_for_track,
    new_project_id,
    projects,
    tracks,
)
from sessions.project_session import ProjectSession


router = APIRouter()


class CreateProjectRequest(BaseModel):
    name: str


@router.post("/projects", response_model=ProjectSession)
def create_project(payload: CreateProjectRequest) -> ProjectSession:
    project = ProjectSession(
        project_id=new_project_id(),
        name=payload.name.strip() or "Untitled Project",
    )
    projects[project.project_id] = project
    return project


@router.get("/projects/{project_id}")
def get_project(project_id: str) -> dict:
    project = get_project_or_404(project_id)
    project_tracks = [track for track in tracks.values() if track.project_id == project_id]
    project_analyses = [analysis for analysis in analyses.values() if analysis.track_id in {t.track_id for t in project_tracks}]
    project_actions = []
    for track in project_tracks:
        project_actions.extend(get_actions_for_track(track.track_id))

    return {
        **project.model_dump(),
        "tracks": [track.model_dump() for track in project_tracks],
        "analyses": [analysis.model_dump() for analysis in project_analyses],
        "actions": [action.model_dump() for action in project_actions],
    }

