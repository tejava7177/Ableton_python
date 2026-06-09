# chordflow-analyzer

`chordflow-analyzer` is a Python prototype for turning local audio files into beat- and bar-aligned chord charts for practice workflows.

## Product Direction

The goal is not to become a perfect chord transcription engine.

The real product goal is to support a workflow like:

`audio -> chord structure -> accompaniment generation -> practice-ready backing`

That means this project needs a chord analysis pipeline that is:

- measurable
- replaceable
- comparable across backends

## Current Architecture

The analyzer now uses a backend-based structure:

- `template`: current librosa/chroma/template baseline
- `chordino`: optional comparison backend stub
- `ensemble`: comparison-oriented wrapper

The baseline backend remains the default so the project still works without optional tools.

## Installation

```bash
cd chordflow-analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Analysis Usage

```bash
python analyze.py \
  --input samples/input.wav \
  --output output/chord_chart.json \
  --backend template \
  --chart-mode simple
```

## Main CLI Options

- `--backend template|chordino|ensemble`
- `--chart-mode simple|detailed`
- `--spelling flat|sharp|auto`
- `--top-k 5`
- `--enable-sequence-smoothing`
- `--disable-sequence-smoothing`
- `--transition-penalty 0.25`
- `--same-chord-bonus 0.15`
- `--save-raw output/raw.json`
- `--chordino-command /path/to/command`
- `--debug`

## Backends

### Template Backend

Backend name:

`librosa-template-baseline`

This backend keeps the current transparent baseline:

- audio loading
- beat tracking
- chroma extraction
- major/minor triad estimation
- slash-bass inference
- lightweight extension inference

It also returns top-k beat candidates for smoothing and analysis.

### Chordino Backend

The Chordino backend is optional.

It is intended as a comparison backend when a compatible external command is available. If unavailable, the CLI prints a clear error message instead of breaking the whole project.

Supported configuration:

- `--chordino-command`
- `CHORDFLOW_CHORDINO_COMMAND`

### Ensemble Backend

The ensemble backend currently wraps the template backend and records whether the optional comparison backend is available. It is designed as a stepping stone for future backend comparison work rather than a fully merged inference system.

## Raw vs Final Output

The backend returns a raw beat-level result:

- tempo
- beat times
- beat-level chords
- top-k beat candidates
- backend metadata

Final chart output is built afterward:

1. optional sequence smoothing
2. bar grouping
3. chart-mode post-processing
4. spelling normalization

You can save the backend raw result with:

```bash
python analyze.py \
  --input samples/input.wav \
  --output output/chart.json \
  --save-raw output/raw.json
```

## Chart Modes

### Simple Mode

Simple mode outputs one representative chord per bar.

- weighted bar vote
- confidence-aware
- intended for practice backing generation

### Detailed Mode

Detailed mode allows multiple chords per bar.

- preserves meaningful changes
- applies short-segment cleanup
- intended for future chord-chart display

## Sequence Smoothing

The project now supports a lightweight Viterbi-style sequence smoother.

If top-k candidates are available:

- use emission scores from beat candidates
- discourage unstable beat-to-beat flips
- prefer staying on the same chord
- slightly prefer common functional or relative transitions

This helps reduce patterns like:

- `Cm C Cm C`
- `G Gm G G`
- `Eb Ebm Eb Eb`

## Evaluation

Create a ground truth file such as:

```json
{
  "title": "samplemusic_ground_truth",
  "bars": [
    { "bar": 1, "chords": ["Eb"] },
    { "bar": 2, "chords": ["Gm"] },
    { "bar": 3, "chords": ["Db"] },
    { "bar": 4, "chords": ["Dm", "G"] }
  ]
}
```

Then run:

```bash
python evaluate.py \
  --prediction output/samplemusic-simple.json \
  --ground-truth ground_truth/samplemusic-bars.json
```

Useful options:

- `--normalize-extensions`
- `--root-only`

The evaluation report includes:

- exact bar accuracy
- first chord root accuracy
- root overlap accuracy
- weighted chord symbol accuracy
- weighted root accuracy
- confusion pairs

## Current Limitations

- This is still not production-grade chord recognition.
- Downbeat detection is approximate.
- The first detected beat is assumed to be bar 1 beat 1.
- Chordino integration is not fully implemented yet.
- Slash chords and extensions are still heuristic.
- Dense orchestration and modulation still produce unstable results.

## Research Direction

The next meaningful improvements are:

- real backend comparison against Chordino or NNLS-Chroma
- stronger sequence decoding
- better relative-major/minor ambiguity handling
- richer timing/downbeat handling
- comparison against more curated ground truth sets
