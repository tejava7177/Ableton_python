"""Global key estimation and diatonic chord priors.

The template matcher scores each beat independently, so it has no sense of
musical context. Most real progressions stay largely within one key, so a soft
prior that nudges ambiguous beats toward in-key chords resolves a large class of
errors (e.g. picking a non-diatonic ``Dm`` where the in-key ``Gm`` was meant).
"""

from __future__ import annotations

import numpy as np

# Krumhansl-Schmuckler key profiles, indexed from the tonic.
_MAJOR_PROFILE = np.array(
    [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
)
_MINOR_PROFILE = np.array(
    [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
)

_PITCH_CLASS_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

# Diatonic triad scale-degrees as (interval_from_tonic, quality) pairs.
# Minor keys include both the natural-minor v and the harmonic-minor V, since
# popular music routinely borrows the major dominant.
_MAJOR_DEGREES = ((0, ""), (2, "m"), (4, "m"), (5, ""), (7, ""), (9, "m"))
_MINOR_DEGREES = ((0, "m"), (3, ""), (5, "m"), (7, "m"), (7, ""), (8, ""), (10, ""))


def _correlate(chroma_mean: np.ndarray, profile: np.ndarray, tonic: int) -> float:
    rotated = np.roll(profile, tonic)
    a = chroma_mean - chroma_mean.mean()
    b = rotated - rotated.mean()
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) / denom)


def estimate_key(chroma: np.ndarray) -> tuple[int, str, float]:
    """Estimate the global key (tonic pitch class, mode, confidence) from chroma.

    ``chroma`` is a 12 x frames matrix; the mean across frames is profiled
    against all 24 major/minor keys.
    """
    chroma_mean = chroma.mean(axis=1) if chroma.ndim == 2 else chroma
    best = (-2.0, 0, "major")
    for tonic in range(12):
        major_score = _correlate(chroma_mean, _MAJOR_PROFILE, tonic)
        minor_score = _correlate(chroma_mean, _MINOR_PROFILE, tonic)
        if major_score > best[0]:
            best = (major_score, tonic, "major")
        if minor_score > best[0]:
            best = (minor_score, tonic, "minor")
    score, tonic, mode = best
    return tonic, mode, score


def diatonic_chord_labels(tonic: int, mode: str) -> set[str]:
    """Return the set of in-key triad labels (e.g. {'Eb', 'Fm', 'Gm', ...})."""
    degrees = _MAJOR_DEGREES if mode == "major" else _MINOR_DEGREES
    labels: set[str] = set()
    for interval, quality in degrees:
        root = _PITCH_CLASS_NAMES[(tonic + interval) % 12]
        labels.add(f"{root}{quality}")
    return labels


def key_name(tonic: int, mode: str) -> str:
    return f"{_PITCH_CLASS_NAMES[tonic]} {mode}"
