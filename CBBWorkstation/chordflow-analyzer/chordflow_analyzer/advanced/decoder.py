"""Key-aware HMM/Viterbi chord decoder.

Per-beat template matching is noisy and context-free. A first-order HMM turns the
whole beat sequence into a single global optimization: each beat prefers the
chord whose template best fits its chroma (emission), while transitions between
beats are shaped by musical priors (self-persistence, staying in key, and common
functional root motion). Viterbi finds the highest-scoring chord path.

The transition model is built once from the estimated key, which generalizes the
ad-hoc bonus heuristics of the original estimator into a single coherent matrix.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np

from ..key_estimator import diatonic_chord_labels, estimate_key, key_name
from .vocabulary import ChordEntry

# Tunable weights (sweepable via env for experiments/measure.py).
EMISSION_TEMPERATURE = float(os.environ.get("CHORDFLOW_EMISSION_TEMP", "0.08"))
EMISSION_DIATONIC_BONUS = float(os.environ.get("CHORDFLOW_EMIT_DIATONIC", "0.12"))
# Bias toward simple triads; an extended chord must beat the triad by at least
# this (times its complexity) on the raw cosine fit to be chosen.
COMPLEXITY_PENALTY = float(os.environ.get("CHORDFLOW_COMPLEXITY", "0.05"))
SELF_TRANSITION = float(os.environ.get("CHORDFLOW_SELF_TRANS", "1.4"))
DIATONIC_BONUS = float(os.environ.get("CHORDFLOW_DIATONIC", "0.9"))
FUNCTIONAL_BONUS = float(os.environ.get("CHORDFLOW_FUNCTIONAL", "0.4"))
CHANGE_PENALTY = float(os.environ.get("CHORDFLOW_CHANGE_PEN", "0.6"))


@dataclass
class DecodedBeat:
    """Result for a single beat."""

    label: str
    score: float
    root_index: int
    suffix: str
    candidates: list[tuple[str, float]]


def _cosine_emission(treble: np.ndarray, templates: np.ndarray) -> np.ndarray:
    """Return (n_beats x n_chords) cosine similarity emission scores."""
    tmpl_norm = templates / (np.linalg.norm(templates, axis=1, keepdims=True) + 1e-9)
    beats = treble.T  # n_beats x 12
    beats_norm = beats / (np.linalg.norm(beats, axis=1, keepdims=True) + 1e-9)
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        sim = beats_norm @ tmpl_norm.T
    return np.nan_to_num(sim, nan=0.0, posinf=0.0, neginf=0.0)


def _build_transition_matrix(vocabulary: list[ChordEntry], diatonic: set[str]) -> np.ndarray:
    """Build an (n x n) additive transition score matrix from musical priors."""
    n = len(vocabulary)
    trans = np.full((n, n), -CHANGE_PENALTY, dtype=np.float64)
    for j, target in enumerate(vocabulary):
        target_in_key = target.label in diatonic
        for i, source in enumerate(vocabulary):
            if i == j:
                trans[i, j] = SELF_TRANSITION
                continue
            score = -CHANGE_PENALTY
            if target_in_key:
                score += DIATONIC_BONUS
            # Functional root motion: fourths/fifths are the backbone of tonal
            # progressions; reward them when both chords are in key.
            interval = (target.root_index - source.root_index) % 12
            if interval in (5, 7) and source.label in diatonic and target_in_key:
                score += FUNCTIONAL_BONUS
            trans[i, j] = score
    return trans


def _viterbi(emission: np.ndarray, transition: np.ndarray) -> np.ndarray:
    """Standard Viterbi; returns the chosen chord index per beat."""
    n_beats, n_chords = emission.shape
    scores = np.zeros((n_beats, n_chords), dtype=np.float64)
    backpointers = np.zeros((n_beats, n_chords), dtype=np.int64)

    scores[0] = emission[0]
    for t in range(1, n_beats):
        # total[i, j] = scores[t-1, i] + transition[i, j]
        total = scores[t - 1][:, None] + transition
        best_prev = np.argmax(total, axis=0)
        scores[t] = emission[t] + total[best_prev, np.arange(n_chords)]
        backpointers[t] = best_prev

    path = np.zeros(n_beats, dtype=np.int64)
    path[-1] = int(np.argmax(scores[-1]))
    for t in range(n_beats - 1, 0, -1):
        path[t - 1] = backpointers[t, path[t]]
    return path


def decode(
    features_treble: np.ndarray,
    global_chroma: np.ndarray,
    vocabulary: list[ChordEntry],
    templates: np.ndarray,
    top_k: int = 5,
    debug: bool = False,
) -> tuple[list[DecodedBeat], dict]:
    """Decode a beat-synchronous chord sequence via key-aware Viterbi."""
    tonic, mode, key_score = estimate_key(global_chroma)
    diatonic = diatonic_chord_labels(tonic, mode)
    if debug:
        print(f"[advanced] key={key_name(tonic, mode)} score={key_score:.3f} diatonic={sorted(diatonic)}")

    emission_raw = _cosine_emission(features_treble, templates)  # n_beats x n_chords
    # Apply the diatonic prior directly to emission (proven effective in the
    # baseline), so in-key chords get a head start before temporal smoothing.
    diatonic_mask = np.array([entry.label in diatonic for entry in vocabulary], dtype=np.float64)
    complexity = np.array([entry.complexity for entry in vocabulary], dtype=np.float64)
    emission_raw = (
        emission_raw
        + EMISSION_DIATONIC_BONUS * diatonic_mask[None, :]
        - COMPLEXITY_PENALTY * complexity[None, :]
    )
    emission = emission_raw / EMISSION_TEMPERATURE
    transition = _build_transition_matrix(vocabulary, diatonic)

    path = _viterbi(emission, transition)

    results: list[DecodedBeat] = []
    for beat_index in range(emission_raw.shape[0]):
        chosen = int(path[beat_index])
        ranked = np.argsort(emission_raw[beat_index])[::-1][:top_k]
        candidates = [(vocabulary[idx].label, float(emission_raw[beat_index, idx])) for idx in ranked]
        entry = vocabulary[chosen]
        results.append(
            DecodedBeat(
                label=entry.label,
                score=float(emission_raw[beat_index, chosen]),
                root_index=entry.root_index,
                suffix=entry.suffix,
                candidates=candidates,
            )
        )

    metadata = {"key": key_name(tonic, mode), "key_score": round(key_score, 3)}
    return results, metadata
