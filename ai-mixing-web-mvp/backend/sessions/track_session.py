from __future__ import annotations

from pydantic import BaseModel


class TrackSession(BaseModel):
    track_id: str
    project_id: str
    filename: str
    file_path: str
    file_url: str
    status: str = "uploaded"

