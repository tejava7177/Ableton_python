"""Template definitions for simple major/minor chord matching."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

PITCH_CLASS_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


@dataclass(frozen=True)
class ChordTemplate:
    """Simple chord template for template matching."""

    label: str
    vector: np.ndarray


def _rotated_template(intervals: tuple[int, ...], root: int) -> np.ndarray:
    vector = np.zeros(12, dtype=np.float64)
    for interval in intervals:
        vector[(root + interval) % 12] = 1.0
    return vector / np.linalg.norm(vector)


def build_templates() -> list[ChordTemplate]:
    """Build major and minor triad templates for all pitch classes."""
    templates: list[ChordTemplate] = []
    for index, name in enumerate(PITCH_CLASS_NAMES):
        templates.append(ChordTemplate(label=name, vector=_rotated_template((0, 4, 7), index)))
        templates.append(ChordTemplate(label=f"{name}m", vector=_rotated_template((0, 3, 7), index)))
    return templates
