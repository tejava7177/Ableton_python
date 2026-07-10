#!/usr/bin/env python3
"""Pretty-print a chord chart JSON as a timestamped, bar-grouped grid.

Useful for ear-checking a prediction against the actual song: each row is one
musical line, with the bar's start time so you can seek to it.

Usage:
    python experiments/show_chart.py output/samplemusic-simple.json
    python experiments/show_chart.py output/samplemusic-simple.json --per-line 4
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _mmss(seconds: float) -> str:
    minutes = int(seconds // 60)
    return f"{minutes}:{seconds - minutes * 60:05.2f}"


def _bar_label(bar: dict) -> str:
    chords = bar.get("chords", [])
    labels = [c["chord"] if isinstance(c, dict) else c for c in chords] or ["-"]
    return " ".join(labels)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pretty-print a chord chart JSON.")
    parser.add_argument("chart", help="Path to a chart JSON produced by analyze.py.")
    parser.add_argument("--per-line", type=int, default=4, help="Bars per printed line.")
    args = parser.parse_args()

    data = json.loads(Path(args.chart).read_text(encoding="utf-8"))
    bars = data.get("bars", [])

    print(f"{data.get('title','?')}  |  key={data.get('key','?')}  tempo={data.get('tempo','?')}  "
          f"bars={len(bars)}  backend={data.get('backend','?')}")
    print("-" * 72)

    for i in range(0, len(bars), args.per_line):
        line = bars[i : i + args.per_line]
        stamp = _mmss(line[0].get("start", 0.0))
        cells = " | ".join(f"{_bar_label(b):<10}" for b in line)
        print(f"{stamp:>7}  | {cells} |")


if __name__ == "__main__":
    main()
