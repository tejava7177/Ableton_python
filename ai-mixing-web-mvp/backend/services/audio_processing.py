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


def apply_channel_eq(
    input_path: str | Path,
    output_path: str | Path,
    *,
    low_cut_hz: float,
    high_cut_hz: float,
    bands: list[dict],
) -> None:
    audio, sample_rate = sf.read(str(input_path), always_2d=True)
    processed = audio.astype(np.float32)

    processed = _apply_high_pass(processed, sample_rate, low_cut_hz)

    for band in bands:
        if not band.get("enabled", True):
            continue
        processed = _apply_peaking_eq(
            processed,
            sample_rate,
            center_hz=float(band["frequency_hz"]),
            gain_db=float(band["gain_db"]),
            q=float(band["q"]),
        )

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


def _apply_peaking_eq(
    audio: np.ndarray,
    sample_rate: int,
    *,
    center_hz: float,
    gain_db: float,
    q: float,
) -> np.ndarray:
    nyquist = sample_rate / 2.0
    if center_hz <= 0.0 or center_hz >= nyquist:
        raise ValueError(f"Center frequency must be between 0 and Nyquist ({nyquist:.1f}Hz)")
    if q <= 0.0:
        raise ValueError("Q must be greater than 0.")

    coefficients = _peaking_biquad(center_hz, gain_db, q, sample_rate)
    b = coefficients["b"]
    a = coefficients["a"]
    sos = np.array([[b[0], b[1], b[2], a[0], a[1], a[2]]], dtype=np.float64)
    return sosfiltfilt(sos, audio, axis=0).astype(np.float32)


def _normalized_cutoff(sample_rate: int, cutoff_hz: float) -> float:
    nyquist = sample_rate / 2.0
    if cutoff_hz <= 0.0 or cutoff_hz >= nyquist:
        raise ValueError(f"Cutoff must be between 0 and Nyquist ({nyquist:.1f}Hz)")
    return cutoff_hz / nyquist


def _peaking_biquad(center_hz: float, gain_db: float, q: float, sample_rate: int) -> dict[str, tuple[float, float, float]]:
    amplitude = 10 ** (gain_db / 40.0)
    omega = 2.0 * np.pi * center_hz / sample_rate
    alpha = np.sin(omega) / (2.0 * q)
    cos_omega = np.cos(omega)

    b0 = 1.0 + alpha * amplitude
    b1 = -2.0 * cos_omega
    b2 = 1.0 - alpha * amplitude
    a0 = 1.0 + alpha / amplitude
    a1 = -2.0 * cos_omega
    a2 = 1.0 - alpha / amplitude

    return {
        "b": (b0 / a0, b1 / a0, b2 / a0),
        "a": (1.0, a1 / a0, a2 / a0),
    }
