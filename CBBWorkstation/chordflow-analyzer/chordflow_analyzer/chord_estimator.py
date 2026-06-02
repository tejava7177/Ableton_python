"""Beat-level chord estimation from chroma features."""

from __future__ import annotations

from typing import Iterable

import numpy as np

from .chord_templates import ChordTemplate, PITCH_CLASS_NAMES, build_templates
from .models import BeatChord

NO_CHORD_CONFIDENCE_THRESHOLD = 0.5
BASS_SLASH_THRESHOLD = 0.35
SLASH_MARGIN = 0.08
SUS4_MIN_STRENGTH = 0.58
SUS4_MARGIN = 0.08
SEVENTH_MIN_STRENGTH = 0.54
SEVENTH_MARGIN = 0.05
RELATIVE_SCORE_MARGIN = 0.06
RELATIVE_NOTE_MARGIN = 0.03


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


def _match_template(
    chroma_vector: np.ndarray,
    templates: Iterable[ChordTemplate],
) -> tuple[ChordTemplate | None, float, dict[str, float]]:
    score_map: dict[str, float] = {}
    best_template: ChordTemplate | None = None
    best_confidence = 0.0

    for template in templates:
        confidence = _cosine_similarity(chroma_vector, template.vector)
        score_map[template.label] = confidence
        if confidence > best_confidence:
            best_template = template
            best_confidence = confidence

    if best_confidence < NO_CHORD_CONFIDENCE_THRESHOLD or best_template is None:
        return None, best_confidence, score_map

    return best_template, best_confidence, score_map


def _resolve_slash_bass(template: ChordTemplate | None, bass_vector: np.ndarray) -> str | None:
    if template is None:
        return None

    bass_index = int(np.argmax(bass_vector))
    bass_strength = float(bass_vector[bass_index])
    root_strength = float(bass_vector[template.root_index])
    if bass_strength < BASS_SLASH_THRESHOLD or bass_strength < root_strength + SLASH_MARGIN:
        return None

    chord_tones = {(template.root_index + interval) % 12 for interval in template.intervals}
    if bass_index == template.root_index or bass_index not in chord_tones:
        return None

    return PITCH_CLASS_NAMES[bass_index]


def _relative_minor_index(major_root_index: int) -> int:
    return (major_root_index - 3) % 12


def _relative_major_index(minor_root_index: int) -> int:
    return (minor_root_index + 3) % 12


def _resolve_relative_family(
    template: ChordTemplate | None,
    chroma_vector: np.ndarray,
    score_map: dict[str, float],
    templates_by_label: dict[str, ChordTemplate],
) -> ChordTemplate | None:
    if template is None:
        return None

    label = template.label
    if label.endswith("m"):
        relative_major_index = _relative_major_index(template.root_index)
        relative_major_label = PITCH_CLASS_NAMES[relative_major_index]
        relative_major_score = score_map.get(relative_major_label, 0.0)

        if relative_major_score >= score_map.get(label, 0.0) - RELATIVE_SCORE_MARGIN:
            shared_fifth_strength = float(chroma_vector[(template.root_index + 7) % 12])
            unique_minor_strength = float(chroma_vector[template.root_index])
            unique_major_strength = float(chroma_vector[(relative_major_index + 4) % 12])
            if unique_major_strength > unique_minor_strength + RELATIVE_NOTE_MARGIN and unique_major_strength >= shared_fifth_strength - RELATIVE_NOTE_MARGIN:
                return templates_by_label.get(relative_major_label, template)
        return template

    relative_minor_index = _relative_minor_index(template.root_index)
    relative_minor_label = f"{PITCH_CLASS_NAMES[relative_minor_index]}m"
    relative_minor_score = score_map.get(relative_minor_label, 0.0)

    if relative_minor_score >= score_map.get(label, 0.0) - RELATIVE_SCORE_MARGIN:
        unique_major_strength = float(chroma_vector[(template.root_index + 7) % 12])
        unique_minor_strength = float(chroma_vector[relative_minor_index])
        if unique_minor_strength > unique_major_strength + RELATIVE_NOTE_MARGIN:
            return templates_by_label.get(relative_minor_label, template)

    return template


def _third_strength(template: ChordTemplate, chroma_vector: np.ndarray) -> float:
    third_interval = 3 if template.label.endswith("m") else 4
    return float(chroma_vector[(template.root_index + third_interval) % 12])


def _extension_suffix(template: ChordTemplate, chroma_vector: np.ndarray) -> str:
    root = template.root_index
    fifth_strength = float(chroma_vector[(root + 7) % 12])
    third_strength = _third_strength(template, chroma_vector)
    fourth_strength = float(chroma_vector[(root + 5) % 12])
    minor_seventh_strength = float(chroma_vector[(root + 10) % 12])
    major_seventh_strength = float(chroma_vector[(root + 11) % 12])

    if template.label.endswith("m"):
        if minor_seventh_strength >= SEVENTH_MIN_STRENGTH and minor_seventh_strength >= fifth_strength - SEVENTH_MARGIN:
            return "m7"
        return "m"

    if fourth_strength >= SUS4_MIN_STRENGTH and fourth_strength >= third_strength + SUS4_MARGIN:
        return "sus4"
    if major_seventh_strength >= SEVENTH_MIN_STRENGTH and major_seventh_strength >= minor_seventh_strength + SEVENTH_MARGIN:
        return "maj7"
    if minor_seventh_strength >= SEVENTH_MIN_STRENGTH:
        return "7"
    return ""


def _compose_label(template: ChordTemplate | None, chroma_vector: np.ndarray, bass_vector: np.ndarray) -> tuple[str, str | None]:
    if template is None:
        return "N", None

    root_label = PITCH_CLASS_NAMES[template.root_index]
    suffix = _extension_suffix(template, chroma_vector)
    if suffix == "m":
        chord_label = f"{root_label}m"
    else:
        chord_label = f"{root_label}{suffix}"

    bass_root = _resolve_slash_bass(template, bass_vector)
    if bass_root:
        return f"{chord_label}/{bass_root}", bass_root
    return chord_label, None


def estimate_beat_chords(
    beat_times: np.ndarray,
    chroma: np.ndarray,
    frame_times: np.ndarray,
    bass_chroma: np.ndarray,
    beats_per_bar: int = 4,
    debug: bool = False,
) -> list[BeatChord]:
    """Estimate one chord per beat interval using template matching."""
    templates = build_templates()
    templates_by_label = {template.label: template for template in templates}
    beat_chords: list[BeatChord] = []

    for index, start_time in enumerate(beat_times):
        if index + 1 < len(beat_times):
            end_time = float(beat_times[index + 1])
        elif len(beat_times) > 1:
            end_time = float(start_time + (beat_times[-1] - beat_times[-2]))
        else:
            end_time = float(start_time + 0.5)

        aggregated = _aggregate_chroma_for_interval(chroma, frame_times, float(start_time), end_time)
        aggregated_bass = _aggregate_chroma_for_interval(bass_chroma, frame_times, float(start_time), end_time)
        template, confidence, score_map = _match_template(aggregated, templates)
        template = _resolve_relative_family(template, aggregated, score_map, templates_by_label)
        label, bass_root = _compose_label(template, aggregated, aggregated_bass)

        beat_chords.append(
                BeatChord(
                    beat_index=index,
                    beat_in_bar=(index % beats_per_bar) + 1,
                    time=float(start_time),
                    chord=label,
                    confidence=confidence,
                    source="beat_raw",
                    bass_root=bass_root,
            )
        )

        if debug:
            print(
                f"[debug] beat={index + 1} start={start_time:.3f} end={end_time:.3f} "
                f"chord={label} confidence={confidence:.3f}"
            )

    return beat_chords
