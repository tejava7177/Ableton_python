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

The analyzer uses a backend-based structure:

- `template`: librosa/chroma/template baseline with a key-aware diatonic prior **(default, most accurate on tested material)**
- `advanced`: HQ beat-synchronous chroma + harmonic-aware vocabulary + key-aware HMM/Viterbi decoder; adds a richer chord vocabulary (7ths, sus, dim/aug), inversions, and tuning correction
- `chordino`: optional comparison backend stub
- `ensemble`: comparison-oriented wrapper

The `template` backend remains the default so the project still works without optional tools.

### Accuracy status (samplemusic, 16-bar ground truth)

| backend | exact bar | first-chord root | weighted root |
| --- | --- | --- | --- |
| `template` | 56% | 69% | 55% |
| `advanced` | 50% | 50% | 40% |

The `template` backend is currently more accurate on the strict major/minor metric;
`advanced` is the better platform for richer harmonic detail. Both expose the estimated
`key`, `tempo`, and (advanced) `tuningSemitones` in the output chart for downstream UI use.

These numbers are measured on a single 16-bar ground-truth sample, so differences of a
bar or two are noise-level. Expanding ground truth is the prerequisite for any further
accuracy work — see the measurement harness below.

### Measurement harness

`experiments/measure.py` runs the full pipeline on a fixed sample and prints a one-line
accuracy summary so a code change can be A/B compared immediately:

```bash
python experiments/measure.py --backend template --verbose
python experiments/measure.py --backend advanced --label "my-change"
```

Most tuning knobs in the advanced backend are overridable via `CHORDFLOW_*` environment
variables (see `chordflow_analyzer/advanced/`) for quick sweeps.

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

- `--backend advanced|template|chordino|ensemble`
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

### Advanced Backend

Backend name:

`advanced-hmm`

A from-the-ground-up recognition pipeline:

- harmonic-percussive separation hook + tuning estimation
- beat-synchronous chroma (treble for quality, dedicated bass register for inversions)
- harmonic-aware chord vocabulary across major, minor, 7, m7, maj7, sus2/4, dim, aug
- a complexity prior that keeps the rich vocabulary from fragmenting common triads
- a key-aware HMM decoded with Viterbi, generalizing the baseline's ad-hoc smoothing

It outputs the estimated key and tuning, and preserves inversions and extended qualities
in detailed/raw output. On the current single-sample ground truth it does not yet beat the
`template` baseline on strict major/minor accuracy; it is the stronger platform for future
work once more ground truth exists.

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
