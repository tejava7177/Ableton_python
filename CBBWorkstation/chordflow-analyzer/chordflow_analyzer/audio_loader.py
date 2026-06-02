"""Audio loading utilities."""

from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np


def load_audio(input_path: Path, sample_rate: int = 22050) -> tuple[np.ndarray, int]:
    """Load a local audio file as mono audio."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    try:
        y, sr = librosa.load(str(input_path), sr=sample_rate, mono=True)
    except Exception as exc:  # pragma: no cover - library-specific failure path
        raise ValueError(f"Unsupported or unreadable audio file: {input_path}") from exc

    if y.size == 0:
        raise ValueError(f"Audio file is empty: {input_path}")

    return y, sr
