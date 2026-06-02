"""Bar-based chart building utilities."""

from __future__ import annotations

import math

import numpy as np

from .models import BarChord, BeatChord, ChordChart


def build_chart(
    title: str,
    tempo: float,
    time_signature: str,
    beats_per_bar: int,
    beat_times: np.ndarray,
    beat_chords: list[BeatChord],
) -> ChordChart:
    """Convert beat-level chords into a bar-based chord chart."""
    if len(beat_times) == 0:
        raise ValueError("Cannot build chart without beats.")

    total_bars = math.ceil(len(beat_times) / beats_per_bar)
    bars: list[BarChord] = []

    for bar_index in range(total_bars):
        start_beat_index = bar_index * beats_per_bar
        end_beat_index = min(start_beat_index + beats_per_bar, len(beat_times))
        bar_start = float(beat_times[start_beat_index])

        if end_beat_index < len(beat_times):
            bar_end = float(beat_times[end_beat_index])
        elif len(beat_times) > 1:
            last_interval = float(beat_times[-1] - beat_times[-2])
            bar_end = float(beat_times[-1] + last_interval)
        else:
            bar_end = float(beat_times[-1] + 0.5)

        bars.append(
            BarChord(
                bar=bar_index + 1,
                start=bar_start,
                end=bar_end,
                chords=beat_chords[start_beat_index:end_beat_index],
            )
        )

    return ChordChart(
        title=title,
        tempo=tempo,
        time_signature=time_signature,
        beats_per_bar=beats_per_bar,
        backend="librosa-template-matching",
        bars=bars,
    )
