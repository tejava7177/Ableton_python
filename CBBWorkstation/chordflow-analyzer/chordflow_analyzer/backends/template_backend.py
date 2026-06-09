"""Librosa template-matching baseline backend."""

from __future__ import annotations

from pathlib import Path

from .base import AnalyzerConfig, ChordRecognitionBackend, RawChordResult
from ..audio_loader import load_audio
from ..beat_tracker import track_beats
from ..chord_estimator import estimate_beat_chords
from ..chroma_extractor import extract_chroma


class TemplateBackend(ChordRecognitionBackend):
    """Transparent librosa/chroma/template baseline."""

    name = "librosa-template-baseline"

    def analyze(self, audio_path: str, config: AnalyzerConfig) -> RawChordResult:
        y, sr = load_audio(Path(audio_path))
        tempo, beat_times = track_beats(y, sr)
        chroma, frame_times, bass_chroma = extract_chroma(y, sr, hop_length=config.hop_length)
        beat_chords, beat_candidates = estimate_beat_chords(
            beat_times=beat_times,
            chroma=chroma,
            frame_times=frame_times,
            bass_chroma=bass_chroma,
            beats_per_bar=config.beats_per_bar,
            top_k=config.top_k,
            debug=config.debug,
        )

        return RawChordResult(
            tempo=tempo,
            beat_times=beat_times,
            beat_chords=beat_chords,
            beat_candidates=beat_candidates,
            metadata={"backend": self.name, "sample_rate": sr},
        )
