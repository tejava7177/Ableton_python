"""Temporal sequence smoothing for beat-level chord candidates."""

from __future__ import annotations

from collections import defaultdict
from math import inf

from .backends.base import AnalyzerConfig, ChordCandidate
from .enharmonic import chord_root, normalize_chord_spelling
from .models import BeatChord


def _normalize_for_compare(chord: str) -> str:
    return normalize_chord_spelling(chord, preferred="flat")


def _is_relative_pair(left: str, right: str) -> bool:
    left_norm = _normalize_for_compare(left)
    right_norm = _normalize_for_compare(right)
    pairs = {
        ("Eb", "Cm"),
        ("Bb", "Gm"),
        ("Db", "Bbm"),
        ("Ab", "Fm"),
        ("C", "Am"),
        ("G", "Em"),
        ("D", "Bm"),
        ("A", "F#m"),
        ("E", "C#m"),
        ("B", "G#m"),
    }
    return (left_norm, right_norm) in pairs or (right_norm, left_norm) in pairs


def _transition_bonus(previous: str, current: str, same_chord_bonus: float) -> float:
    if previous == current:
        return same_chord_bonus

    prev_root = chord_root(previous)
    curr_root = chord_root(current)

    if _is_relative_pair(previous, current):
        return same_chord_bonus * 0.6

    common_pairs = {
        ("Dm", "G"),
        ("G", "C"),
        ("G", "Cm"),
        ("Ab", "Bb"),
        ("Bb", "Eb"),
        ("Eb", "Cm"),
        ("Fm", "Bb"),
    }
    if (previous, current) in common_pairs:
        return same_chord_bonus * 0.5

    if prev_root == curr_root:
        return same_chord_bonus * 0.25

    return 0.0


def _build_candidates_from_top1(beat_chords: list[BeatChord]) -> list[list[ChordCandidate]]:
    return [[ChordCandidate(chord=beat.chord, score=beat.confidence)] for beat in beat_chords]


def smooth_candidate_sequence(
    beat_chords: list[BeatChord],
    beat_candidates: list[list[ChordCandidate]],
    config: AnalyzerConfig,
) -> list[BeatChord]:
    """Smooth beat-level chord sequence using a simple Viterbi-style search."""
    if not beat_chords:
        return []

    candidate_grid = beat_candidates or _build_candidates_from_top1(beat_chords)
    candidate_grid = [candidates or [ChordCandidate(chord=beat_chords[index].chord, score=beat_chords[index].confidence)]
                      for index, candidates in enumerate(candidate_grid)]

    scores: list[dict[int, float]] = []
    backpointers: list[dict[int, int | None]] = []

    for beat_index, candidates in enumerate(candidate_grid):
        beat_scores: dict[int, float] = {}
        beat_backpointers: dict[int, int | None] = {}

        for current_index, current in enumerate(candidates):
            emission = current.score
            if beat_index == 0:
                beat_scores[current_index] = emission
                beat_backpointers[current_index] = None
                continue

            best_score = -inf
            best_prev_index: int | None = None
            previous_candidates = candidate_grid[beat_index - 1]
            previous_scores = scores[beat_index - 1]

            for prev_index, previous in enumerate(previous_candidates):
                transition = _transition_bonus(previous.chord, current.chord, config.same_chord_bonus)
                if previous.chord != current.chord:
                    transition -= config.transition_penalty
                candidate_score = previous_scores[prev_index] + emission + transition
                if candidate_score > best_score:
                    best_score = candidate_score
                    best_prev_index = prev_index

            beat_scores[current_index] = best_score
            beat_backpointers[current_index] = best_prev_index

        scores.append(beat_scores)
        backpointers.append(beat_backpointers)

    final_index = max(scores[-1], key=scores[-1].get)
    chosen_indices = [final_index]
    for beat_index in range(len(candidate_grid) - 1, 0, -1):
        previous_index = backpointers[beat_index][chosen_indices[-1]]
        chosen_indices.append(0 if previous_index is None else previous_index)
    chosen_indices.reverse()

    smoothed: list[BeatChord] = []
    for beat_index, candidate_index in enumerate(chosen_indices):
        chosen = candidate_grid[beat_index][candidate_index]
        original = beat_chords[beat_index]
        smoothed.append(
            BeatChord(
                beat_index=original.beat_index,
                beat_in_bar=original.beat_in_bar,
                time=original.time,
                chord=chosen.chord,
                confidence=chosen.score,
                source="sequence_smoothed",
                bass_root=original.bass_root,
            )
        )

    return smoothed
