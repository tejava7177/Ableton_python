"""Key and context helpers."""

from __future__ import annotations

from collections import Counter

from .enharmonic import chord_root
from .models import BeatChord


def estimate_key_context(beat_chords: list[BeatChord]) -> dict:
    """Estimate a soft tonal context from detected chord usage."""
    normalized_chords = [chord.chord for chord in beat_chords if chord.chord != "N"]
    roots = [chord_root(chord) for chord in normalized_chords]
    root_counts = Counter(roots)
    chord_counts = Counter(normalized_chords)

    flat_indicators = {"Eb", "Bb", "Ab", "Fm", "Cm", "Db", "Gb", "Bbm", "Ebm"}
    flat_score = sum(chord_counts.get(chord, 0) for chord in flat_indicators)
    preferred_spelling = "flat" if flat_score > 0 else "sharp"

    tonal_center = root_counts.most_common(3)
    return {
        "preferred_spelling": preferred_spelling,
        "tonal_centers": tonal_center,
        "root_counts": dict(root_counts),
        "chord_counts": dict(chord_counts),
    }
