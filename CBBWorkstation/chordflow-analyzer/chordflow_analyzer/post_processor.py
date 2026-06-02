"""Post-processing utilities for practice-friendly chord charts."""

from __future__ import annotations

from collections import defaultdict

from .enharmonic import chord_root
from .models import BarChord, BeatChord, ChordChart


def _copy_chord(chord: BeatChord, *, new_chord: str | None = None, new_source: str | None = None) -> BeatChord:
    return BeatChord(
        beat_index=chord.beat_index,
        beat_in_bar=chord.beat_in_bar,
        time=chord.time,
        chord=new_chord if new_chord is not None else chord.chord,
        confidence=chord.confidence,
        source=new_source if new_source is not None else chord.source,
        bass_root=chord.bass_root,
    )


def _group_runs(beat_chords: list[BeatChord]) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    start = 0
    while start < len(beat_chords):
        end = start + 1
        while end < len(beat_chords) and beat_chords[end].chord == beat_chords[start].chord:
            end += 1
        runs.append((start, end))
        start = end
    return runs


def _harmonically_similar(left: str, right: str) -> bool:
    if left == "N" or right == "N":
        return False
    return chord_root(left) == chord_root(right)


def smooth_beat_chords(beat_chords: list[BeatChord], min_duration_beats: int) -> list[BeatChord]:
    """Replace short chord runs with surrounding context."""
    if not beat_chords:
        return []
    if min_duration_beats <= 1:
        return [_copy_chord(chord, new_source="beat_smoothed") for chord in beat_chords]

    smoothed = [_copy_chord(chord, new_source="beat_smoothed") for chord in beat_chords]

    changed = True
    while changed:
        changed = False
        runs = _group_runs(smoothed)
        for run_index, (start, end) in enumerate(runs):
            run_length = end - start
            if run_length >= min_duration_beats:
                continue
            if run_index == 0:
                continue

            prev_run = runs[run_index - 1] if run_index > 0 else None
            next_run = runs[run_index + 1] if run_index + 1 < len(runs) else None
            replacement: str | None = None
            replacement_confidence: float | None = None

            if prev_run and next_run:
                prev_chord = smoothed[prev_run[0]].chord
                next_chord = smoothed[next_run[0]].chord
                if prev_chord == next_chord or _harmonically_similar(prev_chord, next_chord):
                    replacement = prev_chord
                    replacement_confidence = max(smoothed[prev_run[0]].confidence, smoothed[next_run[0]].confidence)
                else:
                    prev_len = prev_run[1] - prev_run[0]
                    next_len = next_run[1] - next_run[0]
                    chosen_run = prev_run if prev_len >= next_len else next_run
                    replacement = smoothed[chosen_run[0]].chord
                    replacement_confidence = smoothed[chosen_run[0]].confidence
            elif prev_run:
                replacement = smoothed[prev_run[0]].chord
                replacement_confidence = smoothed[prev_run[0]].confidence
            elif next_run:
                replacement = smoothed[next_run[0]].chord
                replacement_confidence = smoothed[next_run[0]].confidence

            if replacement is None:
                continue

            for beat_index in range(start, end):
                smoothed[beat_index] = BeatChord(
                    beat_index=smoothed[beat_index].beat_index,
                    beat_in_bar=smoothed[beat_index].beat_in_bar,
                    time=smoothed[beat_index].time,
                    chord=replacement,
                    confidence=replacement_confidence if replacement_confidence is not None else smoothed[beat_index].confidence,
                    source="beat_smoothed",
                    bass_root=smoothed[beat_index].bass_root,
                )
            changed = True
            break

    return smoothed


def remove_short_outliers(beat_chords: list[BeatChord]) -> list[BeatChord]:
    """Remove one-beat outliers, especially when surrounded by stable context."""
    if len(beat_chords) < 3:
        return beat_chords

    cleaned = [_copy_chord(chord, new_source="beat_smoothed") for chord in beat_chords]

    for index in range(1, len(cleaned) - 1):
        previous_chord = cleaned[index - 1].chord
        current_chord = cleaned[index].chord
        next_chord = cleaned[index + 1].chord

        if current_chord == previous_chord or current_chord == next_chord:
            continue

        if previous_chord == next_chord or _harmonically_similar(previous_chord, next_chord):
            cleaned[index] = _copy_chord(cleaned[index], new_chord=previous_chord, new_source="beat_smoothed")
            continue

        if cleaned[index].confidence < (cleaned[index - 1].confidence + cleaned[index + 1].confidence) / 2.0:
            replacement = next_chord if cleaned[index + 1].confidence >= cleaned[index - 1].confidence else previous_chord
            cleaned[index] = _copy_chord(cleaned[index], new_chord=replacement, new_source="beat_smoothed")

    return cleaned


def simplify_bar_chords(bar_chords: list[BeatChord]) -> list[BeatChord]:
    """Reduce a bar to meaningful chord changes for display."""
    if not bar_chords:
        return []

    simplified: list[BeatChord] = []
    previous_chord: str | None = None

    for chord in bar_chords:
        if chord.chord == "N" and simplified:
            continue
        if previous_chord is None or chord.chord != previous_chord:
            simplified.append(_copy_chord(chord, new_source="beat_change"))
            previous_chord = chord.chord

    if simplified and simplified[0].chord == "N":
        for chord in simplified[1:]:
            if chord.chord != "N":
                simplified[0] = _copy_chord(chord, new_source="beat_change")
                break

    return simplified[:]


def _clone_chart(chart: ChordChart, bars: list[BarChord], backend_suffix: str) -> ChordChart:
    return ChordChart(
        title=chart.title,
        tempo=chart.tempo,
        time_signature=chart.time_signature,
        beats_per_bar=chart.beats_per_bar,
        backend=f"{chart.backend}+{backend_suffix}",
        bars=bars,
    )


def _bar_vote(bar: BarChord) -> list[BeatChord]:
    weighted_scores: dict[str, float] = defaultdict(float)
    first_occurrence: dict[str, BeatChord] = {}

    for chord in bar.chords:
        if chord.chord != "N":
            weighted_scores[chord.chord] += chord.confidence
            first_occurrence.setdefault(chord.chord, chord)

    if weighted_scores:
        winner = max(weighted_scores.items(), key=lambda item: (item[1], first_occurrence[item[0]].confidence))[0]
        source_chord = first_occurrence[winner]
        return [
            BeatChord(
                beat_index=source_chord.beat_index,
                beat_in_bar=1,
                time=bar.start,
                chord=winner,
                confidence=weighted_scores[winner] / max(1, len([c for c in bar.chords if c.chord == winner])),
                source="bar_vote",
                bass_root=source_chord.bass_root,
            )
        ]

    fallback = bar.chords[0] if bar.chords else BeatChord(0, 1, bar.start, "N", 0.0, "bar_vote")
    return [
        BeatChord(
            beat_index=fallback.beat_index,
            beat_in_bar=1,
            time=bar.start,
            chord="N",
            confidence=fallback.confidence,
            source="bar_vote",
            bass_root=fallback.bass_root,
        )
    ]


def build_practice_chart(
    raw_chart: ChordChart,
    chart_mode: str,
    min_duration_beats: int = 1,
) -> ChordChart:
    """Convert raw beat-level bars into simple or detailed practice charts."""
    processed_bars: list[BarChord] = []
    for bar in raw_chart.bars:
        processed_beat_chords = remove_short_outliers(
            smooth_beat_chords(bar.chords, min_duration_beats=min_duration_beats)
        )

        if chart_mode == "simple":
            output_chords = _bar_vote(BarChord(bar.bar, bar.start, bar.end, processed_beat_chords))
        else:
            output_chords = simplify_bar_chords(processed_beat_chords)
            if output_chords:
                first_meaningful = next((ch for ch in output_chords if ch.chord != "N"), output_chords[0])
                if output_chords[0].chord == "N" and first_meaningful.chord != "N":
                    output_chords[0] = _copy_chord(first_meaningful, new_source="beat_change")

        processed_bars.append(BarChord(bar=bar.bar, start=bar.start, end=bar.end, chords=output_chords))

    return _clone_chart(raw_chart, processed_bars, backend_suffix=f"post-{chart_mode}")
