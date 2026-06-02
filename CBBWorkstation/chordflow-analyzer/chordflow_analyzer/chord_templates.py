"""Template definitions for core chord matching."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

PITCH_CLASS_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


@dataclass(frozen=True)
class ChordTemplate:
    """Chord template for template matching."""

    label: str
    vector: np.ndarray
    root_index: int
    intervals: tuple[int, ...]


def _rotated_template(intervals: tuple[int, ...], root: int) -> np.ndarray:
    vector = np.zeros(12, dtype=np.float64)
    for interval in intervals:
        vector[(root + interval) % 12] = 1.0
    return vector / np.linalg.norm(vector)


def build_templates() -> list[ChordTemplate]:
    """Build core major/minor triad templates for all pitch classes."""
    templates: list[ChordTemplate] = []
    chord_definitions = (
        ("", (0, 4, 7)),
        ("m", (0, 3, 7)),
    )

    for index, name in enumerate(PITCH_CLASS_NAMES):
        for suffix, intervals in chord_definitions:
            templates.append(
                ChordTemplate(
                    label=f"{name}{suffix}",
                    vector=_rotated_template(intervals, index),
                    root_index=index,
                    intervals=intervals,
                )
            )
    return templates
