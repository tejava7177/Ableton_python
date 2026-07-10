"""Advanced backend: HQ beat-sync chroma + harmonic vocabulary + key-aware HMM."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np

from .base import AnalyzerConfig, ChordCandidate, ChordRecognitionBackend, RawChordResult
from ..advanced.decoder import decode
from ..advanced.features import extract_beat_sync_features
from ..advanced.vocabulary import PITCH_CLASS_NAMES, build_vocabulary, template_matrix
from ..audio_loader import load_audio
from ..beat_tracker import track_beats
from ..models import BeatChord

# Bass must clearly beat the root in the low register before we call an inversion.
BASS_SLASH_MIN = float(os.environ.get("CHORDFLOW_BASS_MIN", "0.30"))
BASS_SLASH_MARGIN = float(os.environ.get("CHORDFLOW_BASS_MARGIN", "0.12"))


def _resolve_slash(root_index: int, intervals: tuple[int, ...], bass_vector: np.ndarray) -> str | None:
    bass_index = int(np.argmax(bass_vector))
    if bass_index == root_index:
        return None
    bass_strength = float(bass_vector[bass_index])
    root_strength = float(bass_vector[root_index])
    if bass_strength < BASS_SLASH_MIN or bass_strength < root_strength + BASS_SLASH_MARGIN:
        return None
    chord_tones = {(root_index + interval) % 12 for interval in intervals}
    if bass_index not in chord_tones:
        return None
    return PITCH_CLASS_NAMES[bass_index]


class AdvancedBackend(ChordRecognitionBackend):
    """Higher-accuracy recognition pipeline."""

    name = "advanced-hmm"

    def analyze(self, audio_path: str, config: AnalyzerConfig) -> RawChordResult:
        y, sr = load_audio(Path(audio_path))
        tempo, beat_times = track_beats(y, sr)

        features = extract_beat_sync_features(y, sr, beat_times, hop_length=config.hop_length)
        vocabulary = build_vocabulary()
        entry_by_label = {entry.label: entry for entry in vocabulary}
        templates = template_matrix(vocabulary)
        decoded, decode_meta = decode(
            features.treble,
            features.global_chroma,
            vocabulary,
            templates,
            top_k=config.top_k,
            debug=config.debug,
        )

        beat_chords: list[BeatChord] = []
        beat_candidates: list[list[ChordCandidate]] = []
        for index, beat in enumerate(decoded):
            entry = entry_by_label[beat.label]
            bass_root = _resolve_slash(beat.root_index, entry.intervals, features.bass[:, index])
            label = f"{beat.label}/{bass_root}" if bass_root else beat.label

            candidates = [ChordCandidate(chord=lbl, score=score) for lbl, score in beat.candidates]
            beat_chords.append(
                BeatChord(
                    beat_index=index,
                    beat_in_bar=(index % config.beats_per_bar) + 1,
                    time=float(beat_times[index]),
                    chord=label,
                    confidence=beat.score,
                    source="advanced_viterbi",
                    bass_root=bass_root,
                    candidates=[candidate.to_dict() for candidate in candidates],
                )
            )
            beat_candidates.append(candidates)

        metadata = {"backend": self.name, "sample_rate": sr, "tuning": round(features.tuning, 4)}
        metadata.update(decode_meta)
        return RawChordResult(
            tempo=tempo,
            beat_times=beat_times,
            beat_chords=beat_chords,
            beat_candidates=beat_candidates,
            metadata=metadata,
        )
