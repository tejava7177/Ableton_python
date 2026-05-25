from pathlib import Path
from typing import Tuple

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt


AUDIO_FILE_SIZE_LIMIT_BYTES = 50 * 1024 * 1024
FILTER_ORDER = 4


def load_audio(file_path: Path) -> Tuple[np.ndarray, int]:
    audio, sample_rate = sf.read(str(file_path), always_2d=True)
    return audio.astype(np.float32), sample_rate


def _dbfs(value: float) -> float:
    safe_value = max(value, 1e-12)
    return round(20 * np.log10(safe_value), 2)


def analyze_audio(audio: np.ndarray, sample_rate: int) -> dict:
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(np.square(audio))))
    duration = float(audio.shape[0] / sample_rate)

    return {
        "duration": round(duration, 2),
        "sample_rate": sample_rate,
        "channels": int(audio.shape[1]),
        "peak_dbfs": _dbfs(peak),
        "rms_dbfs": _dbfs(rms),
    }


def _validate_cutoff(sample_rate: int, cutoff_hz: float) -> float:
    nyquist = sample_rate / 2
    if cutoff_hz <= 0 or cutoff_hz >= nyquist:
        raise ValueError(f"Cutoff must be between 0 and Nyquist ({nyquist:.1f}Hz).")
    return cutoff_hz / nyquist


def apply_high_pass(audio: np.ndarray, sample_rate: int, cutoff_hz: float) -> np.ndarray:
    normalized_cutoff = _validate_cutoff(sample_rate, cutoff_hz)
    sos = butter(FILTER_ORDER, normalized_cutoff, btype="highpass", output="sos")
    return sosfiltfilt(sos, audio, axis=0).astype(np.float32)


def apply_low_pass(audio: np.ndarray, sample_rate: int, cutoff_hz: float) -> np.ndarray:
    normalized_cutoff = _validate_cutoff(sample_rate, cutoff_hz)
    sos = butter(FILTER_ORDER, normalized_cutoff, btype="lowpass", output="sos")
    return sosfiltfilt(sos, audio, axis=0).astype(np.float32)


def save_audio(audio: np.ndarray, sample_rate: int, output_path: Path) -> None:
    peak = float(np.max(np.abs(audio)))
    safe_audio = audio
    if peak > 1.0:
        safe_audio = audio / peak
    sf.write(str(output_path), safe_audio, sample_rate, subtype="PCM_16")
