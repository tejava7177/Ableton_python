from pathlib import Path
from typing import List, Tuple

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt


AUDIO_FILE_SIZE_LIMIT_BYTES = 50 * 1024 * 1024
FILTER_ORDER = 4
DEFAULT_FRAME_MS = 20
DEFAULT_HOP_MS = 10
DEFAULT_FADE_MS = 8


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


def _to_mono(audio: np.ndarray) -> np.ndarray:
    if audio.shape[1] == 1:
        return audio[:, 0]
    return np.mean(audio, axis=1)


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


def calculate_frame_rms(
    audio: np.ndarray,
    sample_rate: int,
    frame_ms: int = DEFAULT_FRAME_MS,
    hop_ms: int = DEFAULT_HOP_MS,
) -> Tuple[np.ndarray, np.ndarray]:
    mono_audio = _to_mono(audio)
    total_samples = len(mono_audio)
    frame_samples = max(1, int(sample_rate * frame_ms / 1000))
    hop_samples = max(1, int(sample_rate * hop_ms / 1000))

    starts = np.arange(0, total_samples, hop_samples, dtype=np.int64)
    rms_values = []

    for start in starts:
        end = min(start + frame_samples, total_samples)
        frame = mono_audio[start:end]
        if len(frame) < frame_samples:
            frame = np.pad(frame, (0, frame_samples - len(frame)))
        rms_values.append(float(np.sqrt(np.mean(np.square(frame)))))

    return starts, np.array(rms_values, dtype=np.float32)


def classify_silence_regions(regions: List[dict], duration: float) -> List[dict]:
    classified_regions = []
    epsilon = max(duration * 1e-6, 1e-4)

    for region in regions:
        region_type = "internal"
        if region["start"] <= epsilon:
            region_type = "start"
        elif region["end"] >= duration - epsilon:
            region_type = "end"

        classified_regions.append(
            {
                "start": round(region["start"], 3),
                "end": round(region["end"], 3),
                "duration": round(region["duration"], 3),
                "type": region_type,
            }
        )

    return classified_regions


def detect_silence_regions(
    audio: np.ndarray,
    sample_rate: int,
    threshold_db: float,
    min_silence_ms: int,
    frame_ms: int = DEFAULT_FRAME_MS,
    hop_ms: int = DEFAULT_HOP_MS,
) -> List[dict]:
    starts, rms_values = calculate_frame_rms(audio, sample_rate, frame_ms, hop_ms)
    total_samples = audio.shape[0]
    frame_samples = max(1, int(sample_rate * frame_ms / 1000))
    min_silence_samples = int(sample_rate * min_silence_ms / 1000)
    threshold_linear = 10 ** (threshold_db / 20)
    is_silence = rms_values <= threshold_linear

    raw_regions = []
    run_start = None

    for idx, silent in enumerate(is_silence):
        if silent and run_start is None:
            run_start = idx
        elif not silent and run_start is not None:
            start_sample = int(starts[run_start])
            end_sample = int(min(starts[idx - 1] + frame_samples, total_samples))
            duration_samples = end_sample - start_sample
            if duration_samples >= min_silence_samples:
                raw_regions.append(
                    {
                        "start": start_sample / sample_rate,
                        "end": end_sample / sample_rate,
                        "duration": duration_samples / sample_rate,
                    }
                )
            run_start = None

    if run_start is not None:
        start_sample = int(starts[run_start])
        end_sample = total_samples
        duration_samples = end_sample - start_sample
        if duration_samples >= min_silence_samples:
            raw_regions.append(
                {
                    "start": start_sample / sample_rate,
                    "end": end_sample / sample_rate,
                    "duration": duration_samples / sample_rate,
                }
            )

    return classify_silence_regions(raw_regions, total_samples / sample_rate)


def _seconds_to_samples(seconds: float, sample_rate: int) -> int:
    return max(0, int(round(seconds * sample_rate)))


def _slice_region_samples(region: dict, sample_rate: int) -> Tuple[int, int]:
    return _seconds_to_samples(region["start"], sample_rate), _seconds_to_samples(
        region["end"], sample_rate
    )


def _apply_edge_fades(audio: np.ndarray, fade_samples: int) -> np.ndarray:
    if len(audio) == 0 or fade_samples <= 0:
        return audio

    fade_length = min(fade_samples, len(audio) // 2 if len(audio) > 1 else 1)
    if fade_length <= 0:
        return audio

    fade_in = np.linspace(0.0, 1.0, fade_length, dtype=np.float32).reshape(-1, 1)
    fade_out = np.linspace(1.0, 0.0, fade_length, dtype=np.float32).reshape(-1, 1)
    faded_audio = audio.copy()
    faded_audio[:fade_length] *= fade_in
    faded_audio[-fade_length:] *= fade_out
    return faded_audio


def _crossfade_segments(segments: List[np.ndarray], fade_samples: int) -> np.ndarray:
    valid_segments = [segment for segment in segments if len(segment) > 0]
    if not valid_segments:
        return np.zeros((0, 1), dtype=np.float32)

    output = valid_segments[0].astype(np.float32, copy=True)
    for segment in valid_segments[1:]:
        next_segment = segment.astype(np.float32, copy=False)
        crossfade = min(fade_samples, len(output), len(next_segment))
        if crossfade <= 0:
            output = np.concatenate([output, next_segment], axis=0)
            continue

        fade_out = np.linspace(1.0, 0.0, crossfade, dtype=np.float32).reshape(-1, 1)
        fade_in = np.linspace(0.0, 1.0, crossfade, dtype=np.float32).reshape(-1, 1)
        overlap = output[-crossfade:] * fade_out + next_segment[:crossfade] * fade_in
        output = np.concatenate([output[:-crossfade], overlap, next_segment[crossfade:]], axis=0)

    return output


def trim_start_end(
    audio: np.ndarray,
    sample_rate: int,
    regions: List[dict],
    padding_ms: int,
) -> np.ndarray:
    padding_samples = int(sample_rate * padding_ms / 1000)
    start_index = 0
    end_index = audio.shape[0]

    for region in regions:
        region_start, region_end = _slice_region_samples(region, sample_rate)
        if region["type"] == "start":
            start_index = max(start_index, max(0, region_end - padding_samples))
        elif region["type"] == "end":
            end_index = min(end_index, min(audio.shape[0], region_start + padding_samples))

    trimmed = audio[start_index:end_index].copy()
    fade_samples = int(sample_rate * DEFAULT_FADE_MS / 1000)
    return _apply_edge_fades(trimmed, fade_samples).astype(np.float32)


def remove_internal_silence(
    audio: np.ndarray,
    sample_rate: int,
    regions: List[dict],
    padding_ms: int,
) -> np.ndarray:
    total_samples = audio.shape[0]
    padding_samples = int(sample_rate * padding_ms / 1000)
    cut_ranges: List[Tuple[int, int]] = []

    for region in regions:
        region_start, region_end = _slice_region_samples(region, sample_rate)

        if region["type"] == "start":
            cut_start = 0
            cut_end = max(0, region_end - padding_samples)
        elif region["type"] == "end":
            cut_start = min(total_samples, region_start + padding_samples)
            cut_end = total_samples
        else:
            cut_start = min(total_samples, region_start + padding_samples)
            cut_end = max(0, region_end - padding_samples)

        if cut_end > cut_start:
            cut_ranges.append((cut_start, cut_end))

    if not cut_ranges:
        return audio.copy()

    cut_ranges.sort()
    merged_cuts: List[Tuple[int, int]] = []
    for start, end in cut_ranges:
        if not merged_cuts or start > merged_cuts[-1][1]:
            merged_cuts.append((start, end))
        else:
            previous_start, previous_end = merged_cuts[-1]
            merged_cuts[-1] = (previous_start, max(previous_end, end))

    segments = []
    cursor = 0
    for cut_start, cut_end in merged_cuts:
        if cut_start > cursor:
            segments.append(audio[cursor:cut_start].copy())
        cursor = cut_end
    if cursor < total_samples:
        segments.append(audio[cursor:].copy())

    fade_samples = int(sample_rate * DEFAULT_FADE_MS / 1000)
    return _crossfade_segments(segments, fade_samples).astype(np.float32)


def shorten_internal_silence(
    audio: np.ndarray,
    sample_rate: int,
    regions: List[dict],
    padding_ms: int,
) -> np.ndarray:
    total_samples = audio.shape[0]
    padding_samples = int(sample_rate * padding_ms / 1000)
    replacement_samples = padding_samples
    fade_samples = int(sample_rate * DEFAULT_FADE_MS / 1000)
    segments: List[np.ndarray] = []
    cursor = 0

    for region in regions:
        region_start, region_end = _slice_region_samples(region, sample_rate)

        if region["type"] == "start":
            cut_end = max(0, region_end - padding_samples)
            cursor = max(cursor, cut_end)
            continue

        if region["type"] == "end":
            cut_start = min(total_samples, region_start + padding_samples)
            if cut_start > cursor:
                segments.append(audio[cursor:cut_start].copy())
            cursor = total_samples
            break

        keep_until = min(total_samples, region_start + padding_samples)
        if keep_until > cursor:
            segments.append(audio[cursor:keep_until].copy())
        if replacement_samples > 0:
            segments.append(np.zeros((replacement_samples, audio.shape[1]), dtype=np.float32))
        cursor = max(keep_until, max(0, region_end - padding_samples))

    if cursor < total_samples:
        segments.append(audio[cursor:].copy())

    shortened = _crossfade_segments(segments, fade_samples).astype(np.float32)
    return _apply_edge_fades(shortened, fade_samples).astype(np.float32)


def save_audio(audio: np.ndarray, sample_rate: int, output_path: Path) -> None:
    peak = float(np.max(np.abs(audio)))
    safe_audio = audio
    if peak > 1.0:
        safe_audio = audio / peak
    sf.write(str(output_path), safe_audio, sample_rate, subtype="PCM_16")
