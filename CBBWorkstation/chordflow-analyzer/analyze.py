#!/usr/bin/env python3
"""CLI entry point for chordflow-analyzer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from chordflow_analyzer.backends import AnalyzerConfig, BackendUnavailableError, create_backend
from chordflow_analyzer.chart_builder import build_chart
from chordflow_analyzer.enharmonic import normalize_chart_spelling
from chordflow_analyzer.key_context import estimate_key_context
from chordflow_analyzer.post_processor import build_practice_chart
from chordflow_analyzer.sequence_smoother import smooth_candidate_sequence


def _format_key_context(key_context: dict) -> str | None:
    """Approximate key label from chord-usage stats (fallback for backends that
    do not estimate a key themselves)."""
    centers = key_context.get("tonal_centers") or []
    if not centers:
        return None
    return f"{centers[0][0]} (tonal center)"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Analyze a local audio file into a chord chart JSON.")
    parser.add_argument("--input", required=True, help="Path to a local audio file.")
    parser.add_argument("--output", required=True, help="Path to the output chord chart JSON.")
    parser.add_argument(
        "--backend",
        choices=("advanced", "template", "chordino", "ensemble"),
        default="template",
        help="Chord recognition backend. 'template' is the most accurate on tested "
        "material; 'advanced' adds a richer vocabulary, inversions, and tuning correction.",
    )
    parser.add_argument("--time-signature", default="4/4", help="Time signature label for output metadata.")
    parser.add_argument("--beats-per-bar", type=int, default=4, help="Beats per bar for chart grouping.")
    parser.add_argument("--hop-length", type=int, default=512, help="Hop length used for chroma extraction.")
    parser.add_argument(
        "--chart-mode",
        choices=("simple", "detailed"),
        default="simple",
        help="Practice chart output mode.",
    )
    parser.add_argument(
        "--spelling",
        choices=("flat", "sharp", "auto"),
        default="auto",
        help="Preferred chord spelling for output.",
    )
    parser.add_argument("--top-k", type=int, default=5, help="Top-k backend chord candidates per beat.")
    parser.add_argument("--enable-sequence-smoothing", action="store_true", default=True, help="Enable sequence smoothing.")
    parser.add_argument("--disable-sequence-smoothing", action="store_true", help="Disable sequence smoothing.")
    parser.add_argument("--transition-penalty", type=float, default=0.25, help="Transition penalty for sequence smoothing.")
    parser.add_argument("--same-chord-bonus", type=float, default=0.15, help="Bonus for staying on the same chord.")
    parser.add_argument("--save-raw", help="Optional path for saving raw backend output JSON.")
    parser.add_argument("--chordino-command", help="Optional chordino/sonic-annotator command path.")
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

    config = AnalyzerConfig(
        time_signature=args.time_signature,
        beats_per_bar=args.beats_per_bar,
        hop_length=args.hop_length,
        min_chord_duration_beats=args.min_chord_duration_beats,
        chart_mode=args.chart_mode,
        spelling=args.spelling,
        debug=args.debug,
        top_k=args.top_k,
        enable_sequence_smoothing=False if args.disable_sequence_smoothing else args.enable_sequence_smoothing,
        transition_penalty=args.transition_penalty,
        same_chord_bonus=args.same_chord_bonus,
        chordino_command=args.chordino_command,
    )

    backend = create_backend(args.backend, config)
    try:
        raw_result = backend.analyze(str(input_path), config)
    except BackendUnavailableError as exc:
        raise SystemExit(str(exc)) from exc

    beat_chords = raw_result.beat_chords
    if config.enable_sequence_smoothing:
        beat_chords = smooth_candidate_sequence(beat_chords, raw_result.beat_candidates, config)

    raw_chart = build_chart(
        title=input_path.stem,
        tempo=raw_result.tempo,
        time_signature=args.time_signature,
        beats_per_bar=args.beats_per_bar,
        beat_times=raw_result.beat_times,
        beat_chords=beat_chords,
    )
    chart = build_practice_chart(
        raw_chart=raw_chart,
        chart_mode=args.chart_mode,
        min_duration_beats=args.min_chord_duration_beats,
    )
    key_context = estimate_key_context(beat_chords)
    preferred_spelling = key_context["preferred_spelling"] if args.spelling == "auto" else args.spelling
    chart = normalize_chart_spelling(chart, preferred=preferred_spelling)

    # Surface song-level context (key, tuning) in the chart so downstream
    # consumers like the workstation UI can display it directly.
    chart_payload = chart.to_dict()
    detected_key = raw_result.metadata.get("key")
    chart_payload["key"] = detected_key if detected_key else _format_key_context(key_context)
    if "tuning" in raw_result.metadata:
        chart_payload["tuningSemitones"] = raw_result.metadata["tuning"]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(chart_payload, handle, indent=2)

    if args.save_raw:
        raw_output_path = Path(args.save_raw)
        raw_output_path.parent.mkdir(parents=True, exist_ok=True)
        raw_payload = {
            "tempo": raw_result.tempo,
            "beatTimes": [round(float(value), 3) for value in raw_result.beat_times],
            "beatChords": [beat.to_dict() for beat in raw_result.beat_chords],
            "beatCandidates": [[candidate.to_dict() for candidate in candidates] for candidates in raw_result.beat_candidates],
            "metadata": raw_result.metadata,
            "keyContext": key_context,
        }
        with raw_output_path.open("w", encoding="utf-8") as handle:
            json.dump(raw_payload, handle, indent=2)

    print(f"Input file: {input_path}")
    print(f"Backend: {backend.name}")
    print(f"Estimated tempo: {raw_result.tempo:.2f}")
    print(f"Number of beats: {len(raw_result.beat_times)}")
    print(f"Number of bars: {len(chart.bars)}")
    print(f"Output path: {output_path}")


if __name__ == "__main__":
    main()
