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
    parser.add_argument("--normalize-extensions", action="store_true", help="Reduce extensions before comparison.")
    parser.add_argument("--root-only", action="store_true", help="Compare roots only.")
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


def reduce_extensions(chord: str) -> str:
    chord = normalize_chord_spelling(chord, preferred="flat")
    if chord == "N":
        return chord
    replacements = [("maj7", ""), ("m7", "m"), ("7", ""), ("sus4", "")]
    for before, after in replacements:
        chord = chord.replace(before, after)
    return chord


def normalize_sequence(chords: list[str], normalize_extensions: bool = False, root_only: bool = False) -> list[str]:
    normalized = [normalize_chord_spelling(chord, preferred="flat") for chord in chords]
    if normalize_extensions:
        normalized = [reduce_extensions(chord) for chord in normalized]
    if root_only:
        normalized = [chord_root(chord) for chord in normalized]
    return normalized


def roots_only(chords: list[str], normalize_extensions: bool = False) -> list[str]:
    return [chord_root(chord) for chord in normalize_sequence(chords, normalize_extensions=normalize_extensions)]


def get_bar_chords(bar: dict) -> list[str]:
    values = bar.get("chords", [])
    if values and isinstance(values[0], dict):
        return [value["chord"] for value in values]
    return values


def evaluate(prediction: dict, ground_truth: dict, normalize_extensions: bool = False, root_only: bool = False) -> dict[str, int | float | dict]:
    predicted_bars = {bar["bar"]: bar for bar in prediction.get("bars", [])}
    ground_truth_bars = {bar["bar"]: bar for bar in ground_truth.get("bars", [])}

    compared_bar_numbers = sorted(set(predicted_bars) & set(ground_truth_bars))
    exact_matches = 0
    first_root_matches = 0
    root_matches = 0
    weighted_symbol_matches = 0
    weighted_root_matches = 0
    total_weight = 0
    confusion_pairs: dict[str, int] = {}

    for bar_number in compared_bar_numbers:
        predicted = normalize_sequence(
            get_bar_chords(predicted_bars[bar_number]),
            normalize_extensions=normalize_extensions,
            root_only=root_only,
        )
        expected = normalize_sequence(
            get_bar_chords(ground_truth_bars[bar_number]),
            normalize_extensions=normalize_extensions,
            root_only=root_only,
        )

        if predicted == expected:
            exact_matches += 1

        predicted_roots = roots_only(predicted, normalize_extensions=normalize_extensions)
        expected_roots = roots_only(expected, normalize_extensions=normalize_extensions)
        if predicted_roots == expected_roots:
            root_matches += 1

        if predicted_roots and expected_roots and predicted_roots[0] == expected_roots[0]:
            first_root_matches += 1

        bar_weight = max(len(expected), 1)
        total_weight += bar_weight
        symbol_matches = sum(1 for index, chord in enumerate(expected) if index < len(predicted) and predicted[index] == chord)
        root_symbol_matches = sum(
            1 for index, chord in enumerate(expected_roots)
            if index < len(predicted_roots) and predicted_roots[index] == chord
        )
        weighted_symbol_matches += symbol_matches
        weighted_root_matches += root_symbol_matches

        max_length = max(len(expected), len(predicted))
        for index in range(max_length):
            predicted_label = predicted[index] if index < len(predicted) else "<missing>"
            expected_label = expected[index] if index < len(expected) else "<extra>"
            if predicted_label != expected_label:
                key = f"{predicted_label} predicted where {expected_label} expected"
                confusion_pairs[key] = confusion_pairs.get(key, 0) + 1

    total_compared = len(compared_bar_numbers)
    missed_bars = len(set(ground_truth_bars) - set(predicted_bars))
    extra_bars = len(set(predicted_bars) - set(ground_truth_bars))

    return {
        "bars_compared": total_compared,
        "exact_bar_accuracy": (exact_matches / total_compared) if total_compared else 0.0,
        "first_chord_root_accuracy": (first_root_matches / total_compared) if total_compared else 0.0,
        "root_overlap_accuracy": (root_matches / total_compared) if total_compared else 0.0,
        "weighted_chord_symbol_accuracy": (weighted_symbol_matches / total_weight) if total_weight else 0.0,
        "weighted_root_accuracy": (weighted_root_matches / total_weight) if total_weight else 0.0,
        "missed_bars": missed_bars,
        "extra_bars": extra_bars,
        "confusion_pairs": dict(sorted(confusion_pairs.items(), key=lambda item: item[1], reverse=True)[:10]),
    }


def main() -> None:
    args = parse_args()
    prediction = load_json(Path(args.prediction))
    ground_truth = load_json(Path(args.ground_truth))
    report = evaluate(
        prediction,
        ground_truth,
        normalize_extensions=args.normalize_extensions,
        root_only=args.root_only,
    )

    print("Evaluation Report")
    print(f"- Bars compared: {report['bars_compared']}")
    print(f"- Exact bar accuracy: {report['exact_bar_accuracy']:.2%}")
    print(f"- First chord root accuracy: {report['first_chord_root_accuracy']:.2%}")
    print(f"- Root overlap accuracy: {report['root_overlap_accuracy']:.2%}")
    print(f"- Weighted chord symbol accuracy: {report['weighted_chord_symbol_accuracy']:.2%}")
    print(f"- Weighted root accuracy: {report['weighted_root_accuracy']:.2%}")
    print(f"- Missed bars: {report['missed_bars']}")
    print(f"- Extra bars: {report['extra_bars']}")
    print("- Confusion pairs:")
    for label, count in report["confusion_pairs"].items():
        print(f"  - {label}: {count} times")


if __name__ == "__main__":
    main()
