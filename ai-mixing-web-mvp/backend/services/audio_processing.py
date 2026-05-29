from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt


FILTER_ORDER = 4


def apply_low_high_cut(
    input_path: str | Path,
    output_path: str | Path,
    low_cut_hz: float,
    high_cut_hz: float,
) -> None:
    audio, sample_rate = sf.read(str(input_path), always_2d=True)
    audio = audio.astype(np.float32)

    processed = _apply_high_pass(audio, sample_rate, low_cut_hz)
    processed = _apply_low_pass(processed, sample_rate, high_cut_hz)

    peak = float(np.max(np.abs(processed))) if processed.size > 0 else 0.0
    if peak > 1.0:
        processed = processed / peak

    sf.write(str(output_path), processed, sample_rate)


def _apply_high_pass(audio: np.ndarray, sample_rate: int, cutoff_hz: float) -> np.ndarray:
    normalized = _normalized_cutoff(sample_rate, cutoff_hz)
    sos = butter(FILTER_ORDER, normalized, btype="highpass", output="sos")
    return sosfiltfilt(sos, audio, axis=0).astype(np.float32)


def _apply_low_pass(audio: np.ndarray, sample_rate: int, cutoff_hz: float) -> np.ndarray:
    normalized = _normalized_cutoff(sample_rate, cutoff_hz)
    sos = butter(FILTER_ORDER, normalized, btype="lowpass", output="sos")
    return sosfiltfilt(sos, audio, axis=0).astype(np.float32)


def _normalized_cutoff(sample_rate: int, cutoff_hz: float) -> float:
    nyquist = sample_rate / 2.0
    if cutoff_hz <= 0.0 or cutoff_hz >= nyquist:
        raise ValueError(f"Cutoff must be between 0 and Nyquist ({nyquist:.1f}Hz)")
    return cutoff_hz / nyquist

