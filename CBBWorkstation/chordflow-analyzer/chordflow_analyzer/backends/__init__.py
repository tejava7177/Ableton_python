"""Chord recognition backends."""

from .advanced_backend import AdvancedBackend
from .base import AnalyzerConfig, BackendUnavailableError, ChordRecognitionBackend, RawChordResult
from .chordino_backend import ChordinoBackend
from .ensemble_backend import EnsembleBackend
from .template_backend import TemplateBackend


def create_backend(name: str, config: AnalyzerConfig) -> ChordRecognitionBackend:
    """Create a backend instance from a CLI/backend name."""
    if name == "advanced":
        return AdvancedBackend()
    if name == "template":
        return TemplateBackend()
    if name == "chordino":
        return ChordinoBackend(config.chordino_command)
    if name == "ensemble":
        return EnsembleBackend(config)
    raise ValueError(f"Unsupported backend: {name}")
