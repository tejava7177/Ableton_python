from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf


def load_audio(file_path: str | Path) -> tuple[np.ndarray, int]:
    audio, sample_rate = sf.read(str(file_path), always_2d=True)
    return audio.astype(np.float32), int(sample_rate)


def calculate_peak_dbfs(audio: np.ndarray) -> float:
    peak = float(np.max(np.abs(audio))) if audio.size > 0 else 0.0
    return _linear_to_dbfs(peak)


def calculate_rms_dbfs(audio: np.ndarray) -> float:
    rms = float(np.sqrt(np.mean(np.square(audio)))) if audio.size > 0 else 0.0
    return _linear_to_dbfs(rms)


def analyze_audio(file_path: str | Path) -> dict[str, float | int]:
    audio, sample_rate = load_audio(file_path)
    duration_sec = float(audio.shape[0] / sample_rate) if sample_rate > 0 else 0.0

    return {
        "duration_sec": round(duration_sec, 4),
        "sample_rate": sample_rate,
        "channels": int(audio.shape[1]),
        "peak_dbfs": calculate_peak_dbfs(audio),
        "rms_dbfs": calculate_rms_dbfs(audio),
    }


def _linear_to_dbfs(value: float) -> float:
    safe_value = max(value, 1e-12)
    return round(20.0 * float(np.log10(safe_value)), 4)

