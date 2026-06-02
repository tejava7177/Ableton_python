# chordflow-analyzer

`chordflow-analyzer` is a lightweight Python prototype for turning a local audio file into a practice-friendly beat- and bar-aligned chord chart JSON.

## Goal

This prototype validates an early ChordFlow workflow:

`audio file -> beat structure -> chroma analysis -> raw beat chords -> post-processed practice chart`

The project is designed to test whether imported audio can be converted into chord timing data that is useful for backing generation and practice.

## Why Post-Processing Matters

Raw beat-level chord estimation is noisy. Even when tempo and beat tracking are reasonable, beat-by-beat template matching often produces:

- one-beat harmonic flicker
- enharmonic inconsistency
- unstable minor/major toggling
- too many chord changes for practice use

ChordFlow therefore needs a second layer that converts raw estimates into charts that musicians can actually use.

## Raw Beat-Level Analysis

The analyzer first produces one chord estimate per detected beat interval:

- load audio with `librosa`
- estimate tempo and beat positions
- extract chroma features
- match chroma against major/minor chord templates
- assign one chord label per beat

This raw output is then grouped into bars and simplified.

## Chart Modes

### Simple Mode

`--chart-mode simple`

Simple mode outputs one representative chord per bar.

- chooses the highest weighted bar vote
- weights votes by confidence
- ignores `N` unless the whole bar is `N`
- intended for practice backing generation

Example:

```bash
python analyze.py --input samples/input.wav --output output/chart-simple.json --chart-mode simple
```

### Detailed Mode

`--chart-mode detailed`

Detailed mode allows multiple chord changes inside a bar.

- keeps meaningful chord changes
- removes short outliers
- applies minimum duration smoothing
- always keeps the first meaningful chord in the bar
- intended for future chord chart display

Example:

```bash
python analyze.py --input samples/input.wav --output output/chart-detailed.json --chart-mode detailed --min-chord-duration-beats 2
```

## Spelling Modes

Supported values:

- `--spelling flat`
- `--spelling sharp`
- `--spelling auto`

Default is `auto`.

For this MVP, `auto` prefers flat spellings when the estimated chart includes common flat-side chords such as `Eb`, `Ab`, `Bb`, `Fm`, or `Cm`. Otherwise it prefers sharp spellings.

## Installation

```bash
cd chordflow-analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Analysis Usage

```bash
python analyze.py --input samples/input.wav --output output/chord_chart.json
```

Optional arguments:

- `--time-signature 4/4`
- `--beats-per-bar 4`
- `--hop-length 512`
- `--min-chord-duration-beats 1`
- `--chart-mode simple`
- `--spelling auto`
- `--debug`

## Output Shape

Simple mode example:

```json
{
  "bar": 1,
  "start": 0.557,
  "end": 3.622,
  "chords": [
    {
      "beat": 1,
      "time": 0.557,
      "chord": "Eb",
      "confidence": 0.74,
      "source": "bar_vote"
    }
  ]
}
```

Detailed mode example:

```json
{
  "bar": 4,
  "start": 9.590,
  "end": 12.632,
  "chords": [
    {
      "beat": 1,
      "time": 9.590,
      "chord": "Dm",
      "confidence": 0.81,
      "source": "beat_change"
    },
    {
      "beat": 3,
      "time": 11.122,
      "chord": "G",
      "confidence": 0.78,
      "source": "beat_change"
    }
  ]
}
```

## Evaluation

Create a small ground truth file in `ground_truth/`, for example:

```json
{
  "title": "samplemusic_ground_truth",
  "bars": [
    { "bar": 1, "chords": ["Eb"] },
    { "bar": 2, "chords": ["Bb"] },
    { "bar": 3, "chords": ["Db"] },
    { "bar": 4, "chords": ["Dm", "G"] }
  ]
}
```

Then run:

```bash
python evaluate.py --prediction output/samplemusic-chord-chart.json --ground-truth ground_truth/samplemusic-bars.json
```

The report includes:

- total bars compared
- exact bar match accuracy
- first chord root accuracy
- root overlap accuracy
- missed bars
- extra bars

## Limitations

- This is not production-grade chord recognition.
- Downbeat detection is still approximate.
- The first detected beat is assumed to be bar 1 beat 1.
- Major and minor triads only.
- No 7th chords, slash chords, or richer harmonic vocabulary yet.
- Simple mode is intended for practice backing generation.
- Detailed mode is intended for future chord chart display.
- Accuracy may be unstable on dense mixes, noisy audio, modulation, or complex harmony.

## Future Plan

- Essentia backend for comparison
- madmom backend for comparison
- explicit downbeat detection
- 7th chord support
- slash chord support
- key estimation
- stronger harmony-aware smoothing
