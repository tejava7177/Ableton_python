"""Simple ensemble backend wrapper."""

from __future__ import annotations

from .base import AnalyzerConfig, BackendUnavailableError, ChordRecognitionBackend, RawChordResult
from .chordino_backend import ChordinoBackend
from .template_backend import TemplateBackend


class EnsembleBackend(ChordRecognitionBackend):
    """Comparison-oriented ensemble wrapper.

    Current MVP behavior falls back to the template backend and records whether
    the optional comparison backend was available.
    """

    name = "ensemble-template-chordino"

    def __init__(self, config: AnalyzerConfig) -> None:
        self.template_backend = TemplateBackend()
        self.chordino_backend = ChordinoBackend(config.chordino_command)

    def analyze(self, audio_path: str, config: AnalyzerConfig) -> RawChordResult:
        result = self.template_backend.analyze(audio_path, config)
        try:
            self.chordino_backend.analyze(audio_path, config)
            result.metadata["comparison_backend"] = "chordino-available"
        except BackendUnavailableError as exc:
            result.metadata["comparison_backend"] = str(exc)
        result.metadata["backend"] = self.name
        return result
