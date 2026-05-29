from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ActionSession(BaseModel):
    action_id: str
    track_id: str
    type: str
    status: str = "pending"
    params: dict[str, Any] = Field(default_factory=dict)
    processed_file_url: str | None = None

