#!/usr/bin/env python3
"""Evaluate predicted bar charts against simple ground truth JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from chordflow_analyzer.enharmonic import chord_root, normalize_chord_spelling


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate predicted chord chart JSON against ground truth.")
    parser.add_argument("--prediction", required=True, help="Predicted chart JSON path.")
    parser.add_argument("--ground-truth", required=True, help="Ground truth JSON path.")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(
            f"JSON file is empty: {path}\n"
            "Create a ground truth file like:\n"
            '{\n  "title": "samplemusic_ground_truth",\n  "bars": [\n    { "bar": 1, "chords": ["Eb"] }\n  ]\n}'
        )

    return json.loads(text)


def normalize_sequence(chords: list[str]) -> list[str]:
    return [normalize_chord_spelling(chord, preferred="flat") for chord in chords]


def roots_only(chords: list[str]) -> list[str]:
    return [chord_root(chord) for chord in normalize_sequence(chords)]


def get_bar_chords(bar: dict) -> list[str]:
    values = bar.get("chords", [])
    if values and isinstance(values[0], dict):
        return [value["chord"] for value in values]
    return values


def evaluate(prediction: dict, ground_truth: dict) -> dict[str, int | float]:
    predicted_bars = {bar["bar"]: bar for bar in prediction.get("bars", [])}
    ground_truth_bars = {bar["bar"]: bar for bar in ground_truth.get("bars", [])}

    compared_bar_numbers = sorted(set(predicted_bars) & set(ground_truth_bars))
    exact_matches = 0
    first_root_matches = 0
    root_matches = 0

    for bar_number in compared_bar_numbers:
        predicted = normalize_sequence(get_bar_chords(predicted_bars[bar_number]))
        expected = normalize_sequence(get_bar_chords(ground_truth_bars[bar_number]))

        if predicted == expected:
            exact_matches += 1

        predicted_roots = roots_only(predicted)
        expected_roots = roots_only(expected)
        if predicted_roots == expected_roots:
            root_matches += 1

        if predicted_roots and expected_roots and predicted_roots[0] == expected_roots[0]:
            first_root_matches += 1

    total_compared = len(compared_bar_numbers)
    missed_bars = len(set(ground_truth_bars) - set(predicted_bars))
    extra_bars = len(set(predicted_bars) - set(ground_truth_bars))

    return {
        "bars_compared": total_compared,
        "exact_bar_accuracy": (exact_matches / total_compared) if total_compared else 0.0,
        "first_chord_root_accuracy": (first_root_matches / total_compared) if total_compared else 0.0,
        "root_overlap_accuracy": (root_matches / total_compared) if total_compared else 0.0,
        "missed_bars": missed_bars,
        "extra_bars": extra_bars,
    }


def main() -> None:
    args = parse_args()
    prediction = load_json(Path(args.prediction))
    ground_truth = load_json(Path(args.ground_truth))
    report = evaluate(prediction, ground_truth)

    print("Evaluation Report")
    print(f"- Bars compared: {report['bars_compared']}")
    print(f"- Exact bar accuracy: {report['exact_bar_accuracy']:.2%}")
    print(f"- First chord root accuracy: {report['first_chord_root_accuracy']:.2%}")
    print(f"- Root overlap accuracy: {report['root_overlap_accuracy']:.2%}")
    print(f"- Missed bars: {report['missed_bars']}")
    print(f"- Extra bars: {report['extra_bars']}")


if __name__ == "__main__":
    main()
