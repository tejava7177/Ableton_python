from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectSession(BaseModel):
    project_id: str
    name: str
    status: str = "created"
    track_ids: list[str] = Field(default_factory=list)
    analysis_ids: list[str] = Field(default_factory=list)
    action_ids: list[str] = Field(default_factory=list)

