#!/usr/bin/env python3
"""Fast measurement harness for chord-recognition accuracy experiments.

Runs the full analyze pipeline on a fixed audio file, evaluates the resulting
chart against ground truth, and prints a compact one-line metric summary so a
code change can be A/B compared immediately.

Usage:
    python experiments/measure.py --label "baseline"
    python experiments/measure.py --label "hpss-chroma" --chart-mode simple
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running as `python experiments/measure.py` from the repo root without
# setting PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from chordflow_analyzer.backends import AnalyzerConfig, create_backend
from chordflow_analyzer.chart_builder import build_chart
from chordflow_analyzer.enharmonic import normalize_chart_spelling
from chordflow_analyzer.key_context import estimate_key_context
from chordflow_analyzer.post_processor import build_practice_chart
from chordflow_analyzer.sequence_smoother import smooth_candidate_sequence

from evaluate import evaluate

REPO = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO / "samples" / "samplemusic.mp3"
DEFAULT_TRUTH = REPO / "ground_truth" / "samplemusic-bars.json"


def run_pipeline(input_path: Path, config: AnalyzerConfig, backend_name: str = "template") -> dict:
    """Run the analyze pipeline and return the final chart dict."""
    backend = create_backend(backend_name, config)
    raw = backend.analyze(str(input_path), config)

    beat_chords = raw.beat_chords
    if config.enable_sequence_smoothing:
        beat_chords = smooth_candidate_sequence(beat_chords, raw.beat_candidates, config)

    raw_chart = build_chart(
        title=input_path.stem,
        tempo=raw.tempo,
        time_signature=config.time_signature,
        beats_per_bar=config.beats_per_bar,
        beat_times=raw.beat_times,
        beat_chords=beat_chords,
    )
    chart = build_practice_chart(
        raw_chart=raw_chart,
        chart_mode=config.chart_mode,
        min_duration_beats=config.min_chord_duration_beats,
    )
    key_context = estimate_key_context(beat_chords)
    preferred = key_context["preferred_spelling"] if config.spelling == "auto" else config.spelling
    chart = normalize_chart_spelling(chart, preferred=preferred)
    return chart.to_dict()


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure chord-recognition accuracy on a fixed sample.")
    parser.add_argument("--label", default="run", help="Label for this measurement.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--ground-truth", default=str(DEFAULT_TRUTH))
    parser.add_argument("--backend", default="template", help="Recognition backend (advanced|template).")
    parser.add_argument("--chart-mode", choices=("simple", "detailed"), default="simple")
    parser.add_argument("--no-smoothing", action="store_true")
    parser.add_argument("--save", help="Optional path to save the produced chart JSON.")
    parser.add_argument("--verbose", action="store_true", help="Print per-bar predicted vs expected.")
    args = parser.parse_args()

    config = AnalyzerConfig(
        chart_mode=args.chart_mode,
        spelling="auto",
        enable_sequence_smoothing=not args.no_smoothing,
    )
    chart = run_pipeline(Path(args.input), config, backend_name=args.backend)
    truth = json.loads(Path(args.ground_truth).read_text(encoding="utf-8"))
    report = evaluate(chart, truth)

    if args.save:
        Path(args.save).write_text(json.dumps(chart, indent=2), encoding="utf-8")

    print(
        f"[{args.label}] "
        f"exact={report['exact_bar_accuracy']:.1%} "
        f"root1={report['first_chord_root_accuracy']:.1%} "
        f"rootSet={report['root_overlap_accuracy']:.1%} "
        f"wSym={report['weighted_chord_symbol_accuracy']:.1%} "
        f"wRoot={report['weighted_root_accuracy']:.1%} "
        f"(bars={report['bars_compared']})"
    )

    if args.verbose:
        pred = {b["bar"]: [c["chord"] for c in b["chords"]] for b in chart["bars"]}
        exp = {b["bar"]: b["chords"] for b in truth["bars"]}
        for bar in sorted(exp):
            p = pred.get(bar, ["-"])
            mark = "OK " if p == exp[bar] else "XX "
            print(f"  {mark}bar {bar:2d}: pred={p}  truth={exp[bar]}")
        print("  Top confusion pairs:")
        for label, count in report["confusion_pairs"].items():
            print(f"    - {label}: {count}")


if __name__ == "__main__":
    main()
