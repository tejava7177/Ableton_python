"""Base types for backend-based chord recognition."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np

from ..models import BeatChord


class BackendUnavailableError(RuntimeError):
    """Raised when an optional backend is unavailable."""


@dataclass
class ChordCandidate:
    """Candidate chord hypothesis for a beat."""

    chord: str
    score: float

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {"chord": self.chord, "score": round(self.score, 3)}


@dataclass
class AnalyzerConfig:
    """Shared analyzer configuration."""

    time_signature: str = "4/4"
    beats_per_bar: int = 4
    hop_length: int = 512
    min_chord_duration_beats: int = 1
    chart_mode: str = "simple"
    spelling: str = "auto"
    debug: bool = False
    top_k: int = 5
    enable_sequence_smoothing: bool = True
    transition_penalty: float = 0.25
    same_chord_bonus: float = 0.15
    chordino_command: str | None = None


@dataclass
class RawChordResult:
    """Common raw output from a backend."""

    tempo: float
    beat_times: np.ndarray
    beat_chords: list[BeatChord]
    beat_candidates: list[list[ChordCandidate]] = field(default_factory=list)
    frame_chord_probabilities: list[dict] | None = None
    metadata: dict = field(default_factory=dict)


class ChordRecognitionBackend(ABC):
    """Common backend interface."""

    name: str

    @abstractmethod
    def analyze(self, audio_path: str, config: AnalyzerConfig) -> RawChordResult:
        """Analyze audio and return a backend-independent raw result."""
