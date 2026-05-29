from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AnalysisSession(BaseModel):
    analysis_id: str
    track_id: str
    status: str = "completed"
    result: dict[str, Any] = Field(default_factory=dict)

