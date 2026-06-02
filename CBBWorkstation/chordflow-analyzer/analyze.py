#!/usr/bin/env python3
"""CLI entry point for chordflow-analyzer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from chordflow_analyzer.audio_loader import load_audio
from chordflow_analyzer.beat_tracker import track_beats
from chordflow_analyzer.chart_builder import build_chart
from chordflow_analyzer.chord_estimator import estimate_beat_chords
from chordflow_analyzer.chroma_extractor import extract_chroma


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Analyze a local audio file into a chord chart JSON.")
    parser.add_argument("--input", required=True, help="Path to a local audio file.")
    parser.add_argument("--output", required=True, help="Path to the output chord chart JSON.")
    parser.add_argument("--time-signature", default="4/4", help="Time signature label for output metadata.")
    parser.add_argument("--beats-per-bar", type=int, default=4, help="Beats per bar for chart grouping.")
    parser.add_argument("--hop-length", type=int, default=512, help="Hop length used for chroma extraction.")
    parser.add_argument(
        "--min-chord-duration-beats",
        type=int,
        default=1,
        help="Minimum beat duration before emitting a chord change.",
    )
    parser.add_argument("--debug", action="store_true", help="Print extra debug information.")
    return parser.parse_args()


def main() -> None:
    """Run the CLI workflow."""
    args = parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    y, sr = load_audio(input_path)
    tempo, beat_times = track_beats(y, sr)
    chroma, frame_times = extract_chroma(y, sr, hop_length=args.hop_length)
    beat_chords = estimate_beat_chords(
        beat_times=beat_times,
        chroma=chroma,
        frame_times=frame_times,
        beats_per_bar=args.beats_per_bar,
        min_chord_duration_beats=args.min_chord_duration_beats,
        debug=args.debug,
    )

    chart = build_chart(
        title=input_path.stem,
        tempo=tempo,
        time_signature=args.time_signature,
        beats_per_bar=args.beats_per_bar,
        beat_times=beat_times,
        beat_chords=beat_chords,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(chart.to_dict(), handle, indent=2)

    print(f"Input file: {input_path}")
    print(f"Estimated tempo: {tempo:.2f}")
    print(f"Number of beats: {len(beat_times)}")
    print(f"Number of bars: {len(chart.bars)}")
    print(f"Output path: {output_path}")


if __name__ == "__main__":
    main()
