from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter

from services.storage import (
    analyses,
    get_project_or_404,
    new_project_id,
    projects,
    tracks,
    actions,
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
    analysis_lookup = {analysis.analysis_id: analysis for analysis in analyses.values()}
    action_lookup = {action.action_id: action for action in actions.values()}
    project_analyses = [analysis_lookup[analysis_id] for analysis_id in project.analysis_ids if analysis_id in analysis_lookup]
    project_actions = [action_lookup[action_id] for action_id in project.action_ids if action_id in action_lookup]

    return {
        **project.model_dump(),
        "tracks": [track.model_dump() for track in project_tracks],
        "analyses": [analysis.model_dump() for analysis in project_analyses],
        "actions": [action.model_dump() for action in project_actions],
    }
