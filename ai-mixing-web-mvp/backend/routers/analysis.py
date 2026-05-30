from __future__ import annotations

from fastapi import APIRouter

from services.audio_analysis import analyze_audio
from services.storage import (
    analyses,
    get_analysis_for_track,
    get_project_or_404,
    get_track_or_404,
    new_analysis_id,
)
from sessions.analysis_session import AnalysisSession


router = APIRouter()


@router.post("/tracks/{track_id}/analysis", response_model=AnalysisSession)
def analyze_track(track_id: str) -> AnalysisSession:
    track = get_track_or_404(track_id)
    project = get_project_or_404(track.project_id)

    result = analyze_audio(track.file_path)
    analysis = get_analysis_for_track(track_id)
    if analysis is None:
        analysis = AnalysisSession(
            analysis_id=new_analysis_id(),
            track_id=track_id,
            status="completed",
            result=result,
        )
        analyses[analysis.analysis_id] = analysis
        project.analysis_ids.append(analysis.analysis_id)
    else:
        analysis.status = "completed"
        analysis.result = result

    if track.status == "uploaded":
        track.status = "analyzed"
    return analysis
