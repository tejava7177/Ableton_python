"""Chroma extraction utilities."""

from __future__ import annotations

import librosa
import numpy as np


def extract_chroma(y: np.ndarray, sr: int, hop_length: int = 512) -> tuple[np.ndarray, np.ndarray]:
    """Extract normalized chroma CQT features and corresponding frame times."""
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)
    norms = np.linalg.norm(chroma, axis=0, keepdims=True)
    safe_norms = np.where(norms == 0.0, 1.0, norms)
    normalized = chroma / safe_norms
    frame_times = librosa.frames_to_time(np.arange(normalized.shape[1]), sr=sr, hop_length=hop_length)
    return normalized, frame_times
