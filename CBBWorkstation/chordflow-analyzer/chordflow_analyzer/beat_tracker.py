"""Beat tracking utilities."""

from __future__ import annotations

import librosa
import numpy as np


def track_beats(y: np.ndarray, sr: int) -> tuple[float, np.ndarray]:
    """Estimate tempo and beat times using librosa beat tracking."""
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    if beat_times.size == 0:
        raise ValueError("No beats detected in the audio.")

    return float(tempo), beat_times
