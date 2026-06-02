# chordflow-analyzer

`chordflow-analyzer` is a lightweight Python prototype for turning a local audio file into a beat- and bar-aligned chord chart JSON.

## Goal

This prototype validates an early ChordFlow workflow:

`audio file -> beat structure -> chroma analysis -> chord estimation -> practice-ready chord chart`

The output is intentionally structured around beats and bars rather than coarse per-second chord labels.

## Why Beat/Bar Chord Charts Matter

A chord label every second is often too loose for musical practice. ChordFlow needs timing information that lines up with how musicians think:

- beat positions
- bar boundaries
- chord changes within a bar

This makes it easier to drive future backing generation, looping, and practice features.

## Installation

```bash
cd chordflow-analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python analyze.py --input samples/input.wav --output output/chord_chart.json
```

Optional arguments:

- `--time-signature 4/4`
- `--beats-per-bar 4`
- `--hop-length 512`
- `--min-chord-duration-beats 1`
- `--debug`

## Output Shape

Example:

```json
{
  "title": "input",
  "tempo": 118.6,
  "timeSignature": "4/4",
  "beatsPerBar": 4,
  "backend": "librosa-template-matching",
  "bars": [
    {
      "bar": 1,
      "start": 0.0,
      "end": 2.03,
      "chords": [
        { "beat": 1, "time": 0.0, "chord": "C", "confidence": 0.82 },
        { "beat": 3, "time": 1.02, "chord": "G", "confidence": 0.75 }
      ]
    }
  ]
}
```

## Current Limitations

- The MVP assumes the first detected beat is bar 1 beat 1.
- Downbeat detection is not implemented yet.
- `4/4` is assumed by default.
- Major and minor triads only.
- No 7th chords, slash chords, or richer harmonic vocabulary yet.
- Accuracy may be unstable on dense mixes, noisy audio, modulation, or complex harmony.
- This is for workflow validation, not production-grade chord recognition.

## Future Plan

- Essentia backend for comparison
- madmom backend for comparison
- downbeat detection
- 7th chord support
- slash chord support
- key estimation
- stronger smoothing and bar alignment heuristics

