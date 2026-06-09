"""Optional Chordino/NNLS-Chroma wrapper backend."""

from __future__ import annotations

import os
import shutil

from .base import AnalyzerConfig, BackendUnavailableError, ChordRecognitionBackend, RawChordResult


class ChordinoBackend(ChordRecognitionBackend):
    """Optional backend wrapper around an external Chordino-style command."""

    name = "chordino-nnls-chroma"

    def __init__(self, chordino_command: str | None = None) -> None:
        self.chordino_command = chordino_command or os.getenv("CHORDFLOW_CHORDINO_COMMAND")

    def analyze(self, audio_path: str, config: AnalyzerConfig) -> RawChordResult:
        command = self.chordino_command or shutil.which("sonic-annotator")
        if not command:
            raise BackendUnavailableError(
                "Chordino backend is unavailable. Set --chordino-command or CHORDFLOW_CHORDINO_COMMAND, "
                "or install a compatible tool such as sonic-annotator with Chordino/NNLS-Chroma."
            )

        raise BackendUnavailableError(
            f"Chordino backend command detected ({command}) but parsing/execution is not implemented yet. "
            "Use it as an optional comparison backend once the local command/output format is configured."
        )
