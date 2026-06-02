"""Data models for JSON serialization."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BeatChord:
    """Chord label aligned to a beat."""

    beat_index: int
    beat_in_bar: int
    time: float
    chord: str
    confidence: float

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "beat": self.beat_in_bar,
            "time": round(self.time, 3),
            "chord": self.chord,
            "confidence": round(self.confidence, 3),
        }


@dataclass
class BarChord:
    """A bar entry containing chord change events."""

    bar: int
    start: float
    end: float
    chords: list[BeatChord] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "bar": self.bar,
            "start": round(self.start, 3),
            "end": round(self.end, 3),
            "chords": [chord.to_dict() for chord in self.chords],
        }


@dataclass
class ChordChart:
    """Top-level chart output."""

    title: str
    tempo: float
    time_signature: str
    beats_per_bar: int
    backend: str
    bars: list[BarChord]

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "title": self.title,
            "tempo": round(self.tempo, 3),
            "timeSignature": self.time_signature,
            "beatsPerBar": self.beats_per_bar,
            "backend": self.backend,
            "bars": [bar.to_dict() for bar in self.bars],
        }
