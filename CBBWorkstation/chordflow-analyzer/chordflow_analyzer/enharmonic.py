"""Enharmonic spelling helpers."""

from __future__ import annotations

from .models import BarChord, BeatChord, ChordChart

SHARP_TO_FLAT = {
    "C#": "Db",
    "D#": "Eb",
    "F#": "Gb",
    "G#": "Ab",
    "A#": "Bb",
}

FLAT_TO_SHARP = {value: key for key, value in SHARP_TO_FLAT.items()}


def split_chord_label(chord: str) -> tuple[str, str]:
    """Split a chord into root and suffix."""
    if chord == "N" or not chord:
        return chord, ""

    if "/" in chord:
        left, right = chord.split("/", maxsplit=1)
        root, suffix = split_chord_label(left)
        return root, f"{suffix}/{right}"

    if len(chord) >= 2 and chord[1] in {"#", "b"}:
        return chord[:2], chord[2:]
    return chord[:1], chord[1:]


def chord_root(chord: str) -> str:
    """Extract only the root label from a chord."""
    root, _ = split_chord_label(chord)
    return root


def normalize_chord_spelling(chord: str, preferred: str = "flat") -> str:
    """Convert enharmonic spelling while preserving suffix and quality."""
    root, suffix = split_chord_label(chord)
    if root == "N":
        return "N"

    slash_bass = None
    if "/" in suffix:
        suffix, slash_bass = suffix.split("/", maxsplit=1)

    if preferred == "flat":
        root = SHARP_TO_FLAT.get(root, root)
    elif preferred == "sharp":
        root = FLAT_TO_SHARP.get(root, root)

    if slash_bass:
        if preferred == "flat":
            slash_bass = SHARP_TO_FLAT.get(slash_bass, slash_bass)
        elif preferred == "sharp":
            slash_bass = FLAT_TO_SHARP.get(slash_bass, slash_bass)
        return f"{root}{suffix}/{slash_bass}"

    return f"{root}{suffix}"


def choose_spelling_preference(chart: ChordChart) -> str:
    """Choose a simple display spelling preference from chart content."""
    flat_indicators = {"Eb", "Ab", "Bb", "Fm", "Cm", "Db", "Gb", "Bbm", "Ebm", "Abm"}
    for bar in chart.bars:
        for chord in bar.chords:
            normalized = normalize_chord_spelling(chord.chord, preferred="flat")
            if normalized in flat_indicators:
                return "flat"
    return "sharp"


def normalize_chart_spelling(chart: ChordChart, key: str | None = None, preferred: str = "flat") -> ChordChart:
    """Return a chart copy with normalized enharmonic spelling."""
    resolved_preference = choose_spelling_preference(chart) if preferred == "auto" else preferred
    normalized_bars: list[BarChord] = []

    for bar in chart.bars:
        normalized_bars.append(
            BarChord(
                bar=bar.bar,
                start=bar.start,
                end=bar.end,
                chords=[
                    BeatChord(
                        beat_index=chord.beat_index,
                        beat_in_bar=chord.beat_in_bar,
                        time=chord.time,
                        chord=normalize_chord_spelling(chord.chord, preferred=resolved_preference),
                        confidence=chord.confidence,
                        source=chord.source,
                    )
                    for chord in bar.chords
                ],
            )
        )

    return ChordChart(
        title=chart.title,
        tempo=chart.tempo,
        time_signature=chart.time_signature,
        beats_per_bar=chart.beats_per_bar,
        backend=chart.backend,
        bars=normalized_bars,
    )
