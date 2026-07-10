"""Expanded chord vocabulary with harmonic-aware templates.

Binary triad templates ([root, third, fifth] = 1, else 0) match poorly against
real recordings, because every played note also radiates energy at its
harmonics. A C note, for example, deposits energy not only in C but also in G
(3rd harmonic) and E (5th harmonic). Modelling that makes the templates resemble
actual chroma far more closely, which sharply improves major/minor and
seventh-quality discrimination.

Each chord template is the L1-normalized sum, over its chord tones, of a
harmonic comb whose partials decay geometrically.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np

PITCH_CLASS_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

# Pitch-class offset of the first harmonics of a note (1st..6th partial) and a
# geometric decay weight applied to successive partials.
_HARMONIC_OFFSETS = (0, 12, 19, 24, 28, 31)  # semitones above fundamental
_HARMONIC_DECAY = 0.6

# Chord qualities as (suffix, intervals, complexity). Suffix follows the
# project's existing label convention (minor = "m"). Complexity biases the
# decoder toward plain triads unless an extension is strongly supported, which
# keeps a rich vocabulary from fragmenting common major/minor recognition.
_QUALITIES: tuple[tuple[str, tuple[int, ...], float], ...] = (
    ("", (0, 4, 7), 0.0),          # major
    ("m", (0, 3, 7), 0.0),         # minor
    ("7", (0, 4, 7, 10), 1.0),     # dominant 7
    ("m7", (0, 3, 7, 10), 1.0),    # minor 7
    ("maj7", (0, 4, 7, 11), 1.0),  # major 7
    ("sus4", (0, 5, 7), 1.5),      # suspended 4
    ("sus2", (0, 2, 7), 1.5),      # suspended 2
    ("dim", (0, 3, 6), 1.8),       # diminished
    ("aug", (0, 4, 8), 2.0),       # augmented
)


@dataclass(frozen=True)
class ChordEntry:
    """One chord in the vocabulary."""

    label: str
    root_index: int
    suffix: str
    intervals: tuple[int, ...]
    complexity: float
    template: np.ndarray  # 12-dim, L1-normalized harmonic-weighted profile


# "binary" = pure chord-tone templates (cleaner cosine discrimination);
# "harmonic" = chord tones plus decaying overtone energy.
_TEMPLATE_STYLE = os.environ.get("CHORDFLOW_TEMPLATE", "binary")


def _harmonic_pitch_profile(root: int, intervals: tuple[int, ...]) -> np.ndarray:
    profile = np.zeros(12, dtype=np.float64)
    if _TEMPLATE_STYLE == "binary":
        for interval in intervals:
            profile[(root + interval) % 12] = 1.0
        total = profile.sum()
        return profile / total if total > 0 else profile

    for interval in intervals:
        note = (root + interval) % 12
        weight = 1.0
        for offset in _HARMONIC_OFFSETS:
            profile[(note + offset) % 12] += weight
            weight *= _HARMONIC_DECAY
    total = profile.sum()
    return profile / total if total > 0 else profile


def _active_qualities() -> tuple[tuple[str, tuple[int, ...], float], ...]:
    # Restrict the vocabulary for ablation; default to the full set.
    selected = os.environ.get("CHORDFLOW_QUALITIES")
    if not selected:
        return _QUALITIES
    wanted = {token.strip() for token in selected.split(",")}
    # Allow "maj" as a readable alias for the empty major suffix.
    return tuple(
        (suffix, intervals, complexity)
        for suffix, intervals, complexity in _QUALITIES
        if suffix in wanted or (suffix == "" and "maj" in wanted)
    )


def build_vocabulary() -> list[ChordEntry]:
    """Build the full chord vocabulary (no explicit N entry; handled by decoder)."""
    entries: list[ChordEntry] = []
    for root in range(12):
        for suffix, intervals, complexity in _active_qualities():
            label = f"{PITCH_CLASS_NAMES[root]}{suffix}"
            entries.append(
                ChordEntry(
                    label=label,
                    root_index=root,
                    suffix=suffix,
                    intervals=intervals,
                    complexity=complexity,
                    template=_harmonic_pitch_profile(root, intervals),
                )
            )
    return entries


def template_matrix(vocabulary: list[ChordEntry]) -> np.ndarray:
    """Stack templates into a (n_chords x 12) matrix for vectorized scoring."""
    return np.vstack([entry.template for entry in vocabulary])
