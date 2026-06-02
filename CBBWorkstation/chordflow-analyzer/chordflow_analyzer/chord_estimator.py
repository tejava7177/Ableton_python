"""Beat-level chord estimation from chroma features."""

from __future__ import annotations

from typing import Iterable

import numpy as np

from .chord_templates import ChordTemplate, build_templates
from .models import BeatChord

NO_CHORD_CONFIDENCE_THRESHOLD = 0.5


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) / denom)


def _aggregate_chroma_for_interval(
    chroma: np.ndarray,
    frame_times: np.ndarray,
    start_time: float,
    end_time: float,
) -> np.ndarray:
    mask = (frame_times >= start_time) & (frame_times < end_time)
    if not np.any(mask):
        nearest_index = int(np.argmin(np.abs(frame_times - start_time)))
        return chroma[:, nearest_index]
    return np.mean(chroma[:, mask], axis=1)


def _match_template(chroma_vector: np.ndarray, templates: Iterable[ChordTemplate]) -> tuple[str, float]:
    best_label = "N"
    best_confidence = 0.0
    for template in templates:
        confidence = _cosine_similarity(chroma_vector, template.vector)
        if confidence > best_confidence:
            best_label = template.label
            best_confidence = confidence
    if best_confidence < NO_CHORD_CONFIDENCE_THRESHOLD:
        return "N", best_confidence
    return best_label, best_confidence


def _smooth_beat_chords(chords: list[BeatChord], min_duration_beats: int) -> list[BeatChord]:
    if not chords or min_duration_beats <= 1:
        return chords

    smoothed: list[BeatChord] = []
    run_start = 0

    while run_start < len(chords):
        run_end = run_start + 1
        while run_end < len(chords) and chords[run_end].chord == chords[run_start].chord:
            run_end += 1

        run_length = run_end - run_start
        if run_length < min_duration_beats and smoothed:
            replacement = smoothed[-1].chord
            replacement_confidence = smoothed[-1].confidence
            for index in range(run_start, run_end):
                current = chords[index]
                smoothed.append(
                    BeatChord(
                        beat_index=current.beat_index,
                        beat_in_bar=current.beat_in_bar,
                        time=current.time,
                        chord=replacement,
                        confidence=replacement_confidence,
                    )
                )
        else:
            smoothed.extend(chords[run_start:run_end])

        run_start = run_end

    return smoothed


def estimate_beat_chords(
    beat_times: np.ndarray,
    chroma: np.ndarray,
    frame_times: np.ndarray,
    beats_per_bar: int = 4,
    min_chord_duration_beats: int = 1,
    debug: bool = False,
) -> list[BeatChord]:
    """Estimate one chord per beat interval using template matching."""
    templates = build_templates()
    beat_chords: list[BeatChord] = []

    for index, start_time in enumerate(beat_times):
        if index + 1 < len(beat_times):
            end_time = float(beat_times[index + 1])
        elif len(beat_times) > 1:
            end_time = float(start_time + (beat_times[-1] - beat_times[-2]))
        else:
            end_time = float(start_time + 0.5)

        aggregated = _aggregate_chroma_for_interval(chroma, frame_times, float(start_time), end_time)
        label, confidence = _match_template(aggregated, templates)

        beat_chords.append(
                BeatChord(
                    beat_index=index,
                    beat_in_bar=(index % beats_per_bar) + 1,
                    time=float(start_time),
                    chord=label,
                    confidence=confidence,
            )
        )

        if debug:
            print(
                f"[debug] beat={index + 1} start={start_time:.3f} end={end_time:.3f} "
                f"chord={label} confidence={confidence:.3f}"
            )

    return _smooth_beat_chords(beat_chords, min_chord_duration_beats)
