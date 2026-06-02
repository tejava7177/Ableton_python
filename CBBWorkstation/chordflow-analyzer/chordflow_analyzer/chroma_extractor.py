"""Chroma extraction utilities."""

from __future__ import annotations

import librosa
import numpy as np


def _normalize_columns(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=0, keepdims=True)
    safe_norms = np.where(norms == 0.0, 1.0, norms)
    return matrix / safe_norms


def _extract_bass_chroma(y: np.ndarray, sr: int, hop_length: int) -> np.ndarray:
    cqt = np.abs(
        librosa.cqt(
            y=y,
            sr=sr,
            hop_length=hop_length,
            fmin=librosa.note_to_hz("C2"),
            n_bins=24,
            bins_per_octave=12,
        )
    )

    bass_chroma = np.zeros((12, cqt.shape[1]), dtype=np.float64)
    for bin_index in range(cqt.shape[0]):
        bass_chroma[bin_index % 12] += cqt[bin_index]

    return _normalize_columns(bass_chroma)


def extract_chroma(y: np.ndarray, sr: int, hop_length: int = 512) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract normalized chroma, frame times, and low-register bass chroma."""
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)
    normalized = _normalize_columns(chroma)
    frame_times = librosa.frames_to_time(np.arange(normalized.shape[1]), sr=sr, hop_length=hop_length)
    bass_chroma = _extract_bass_chroma(y, sr, hop_length)
    return normalized, frame_times, bass_chroma
