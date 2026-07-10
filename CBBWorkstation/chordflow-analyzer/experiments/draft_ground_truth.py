#!/usr/bin/env python3
"""Ground-truth drafting tool.

A language model cannot transcribe chords by ear, so ground truth needs a human
in the loop. This tool minimizes that effort: it runs both backends over the
full song and emits (a) a pre-filled ground-truth JSON skeleton and (b) a
human-friendly correction worksheet with per-bar timestamps and an agreement
flag, so the reviewer can jump straight to the bars that need attention.

Bars already present in an existing (verified) ground-truth file are preserved
verbatim and marked as locked; only the remaining bars are drafted.

Usage:
    python experiments/draft_ground_truth.py \
        --input samples/samplemusic.mp3 \
        --existing ground_truth/samplemusic-bars.json \
        --out-json ground_truth/samplemusic-bars.full.draft.json \
        --out-worksheet ground_truth/samplemusic-worksheet.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from chordflow_analyzer.backends import AnalyzerConfig, create_backend
from chordflow_analyzer.chart_builder import build_chart
from chordflow_analyzer.enharmonic import normalize_chart_spelling
from chordflow_analyzer.key_context import estimate_key_context
from chordflow_analyzer.post_processor import build_practice_chart
from chordflow_analyzer.sequence_smoother import smooth_candidate_sequence

REPO = Path(__file__).resolve().parent.parent


def _chart_for_backend(input_path: Path, backend_name: str) -> dict:
    config = AnalyzerConfig(chart_mode="simple", spelling="auto")
    backend = create_backend(backend_name, config)
    raw = backend.analyze(str(input_path), config)
    beat_chords = smooth_candidate_sequence(raw.beat_chords, raw.beat_candidates, config)
    raw_chart = build_chart(
        title=input_path.stem,
        tempo=raw.tempo,
        time_signature=config.time_signature,
        beats_per_bar=config.beats_per_bar,
        beat_times=raw.beat_times,
        beat_chords=beat_chords,
    )
    chart = build_practice_chart(raw_chart=raw_chart, chart_mode="simple")
    key_ctx = estimate_key_context(beat_chords)
    chart = normalize_chart_spelling(chart, preferred=key_ctx["preferred_spelling"])
    payload = chart.to_dict()
    payload["key"] = raw.metadata.get("key", key_ctx.get("preferred_spelling"))
    return payload


def _bar_chord(bar: dict) -> str:
    chords = bar.get("chords", [])
    if not chords:
        return "N"
    return chords[0]["chord"] if isinstance(chords[0], dict) else chords[0]


def _mmss(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = seconds - minutes * 60
    return f"{minutes}:{secs:05.2f}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Draft ground truth from backend predictions.")
    parser.add_argument("--input", default=str(REPO / "samples" / "samplemusic.mp3"))
    parser.add_argument("--existing", default=str(REPO / "ground_truth" / "samplemusic-bars.json"))
    parser.add_argument("--out-json", default=str(REPO / "ground_truth" / "samplemusic-bars.full.draft.json"))
    parser.add_argument("--out-worksheet", default=str(REPO / "ground_truth" / "samplemusic-worksheet.md"))
    args = parser.parse_args()

    input_path = Path(args.input)
    template = _chart_for_backend(input_path, "template")
    advanced = _chart_for_backend(input_path, "advanced")

    existing_bars: dict[int, list[str]] = {}
    existing_path = Path(args.existing)
    if existing_path.exists():
        existing = json.loads(existing_path.read_text(encoding="utf-8"))
        for bar in existing.get("bars", []):
            chords = bar.get("chords", [])
            existing_bars[bar["bar"]] = [c["chord"] if isinstance(c, dict) else c for c in chords]

    template_by_bar = {b["bar"]: b for b in template["bars"]}
    advanced_by_bar = {b["bar"]: b for b in advanced["bars"]}
    all_bars = sorted(set(template_by_bar) | set(advanced_by_bar))

    draft_bars: list[dict] = []
    worksheet_rows: list[str] = []
    agree_count = 0
    locked_count = 0

    for bar_no in all_bars:
        t_chord = _bar_chord(template_by_bar.get(bar_no, {}))
        a_chord = _bar_chord(advanced_by_bar.get(bar_no, {}))
        start = template_by_bar.get(bar_no, advanced_by_bar.get(bar_no, {})).get("start", 0.0)
        agree = t_chord == a_chord

        if bar_no in existing_bars:
            chords = existing_bars[bar_no]
            status = "LOCKED"
            locked_count += 1
        else:
            chords = [t_chord]  # seed with the more accurate backend
            status = "agree" if agree else "CHECK"
        if agree:
            agree_count += 1

        draft_bars.append({"bar": bar_no, "chords": chords})
        worksheet_rows.append(
            f"| {bar_no} | {_mmss(start)} | {status} | {' '.join(chords)} | {t_chord} | {a_chord} | {'=' if agree else 'x'} |"
        )

    draft = {"title": f"{input_path.stem}_ground_truth_draft", "bars": draft_bars}
    Path(args.out_json).write_text(json.dumps(draft, indent=2), encoding="utf-8")

    header = (
        f"# Ground-truth worksheet — {input_path.stem}\n\n"
        f"- Total bars: {len(all_bars)}  |  Locked (already verified): {locked_count}  "
        f"|  Backend agreement: {agree_count}/{len(all_bars)}\n"
        f"- Key (template / advanced): {template.get('key')} / {advanced.get('key')}\n\n"
        "Listen to each non-LOCKED bar at its start time and fix the **Draft** column.\n"
        "`CHECK` = backends disagree (review first). `=` = backends agree (likely correct).\n\n"
        "| Bar | Start | Status | Draft | template | advanced | agree |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
    )
    Path(args.out_worksheet).write_text(header + "\n".join(worksheet_rows) + "\n", encoding="utf-8")

    print(f"Drafted {len(all_bars)} bars ({locked_count} locked, {agree_count} backend-agreements).")
    print(f"JSON draft:  {args.out_json}")
    print(f"Worksheet:   {args.out_worksheet}")


if __name__ == "__main__":
    main()
