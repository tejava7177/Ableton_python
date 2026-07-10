# ChordFlow Workstation

Type a chord progression, pick a style, and hear a full backing band that follows
your chords in real time — a desktop auto-accompaniment workstation.

## What it is

ChordFlow Workstation is a JUCE desktop application inspired by arranger keyboards
(Yamaha Genos, Korg Pa). You enter a chord progression and choose a *style* — a
genre groove — and the app generates and plays a complete accompaniment (drums,
bass, chords, pad) that automatically transposes to follow your chords. Song
sections (Intro, Main A/B, Fill, Ending) can be triggered live, and you can author
your own styles in a built-in pattern editor.

It serves two kinds of users:

- **Performers & songwriters** — enter chords and get an instant band to practice
  or write over.
- **Content designers** — create and edit the styles (accompaniment patterns and
  voices) that drive the instrument.

## Core loop

```
Enter chords → pick a style → press play → a band plays your progression
            → trigger sections live → export MIDI
```

## Key features

- Manual chord progression input with a live chord track
- Built-in styles with drums / bass / chord / pad tracks
- Real-time auto-accompaniment that transposes to follow the chords
- Live arranger sections: Intro, Main A, Main B, Fill, Ending
- Per-track Voice and mix parameters (instrument, volume, pan, octave)
- Groove controls (tempo, swing, energy)
- Style editor: author patterns per section on a step grid
- MIDI export of the arranged result
- Self-contained audio via built-in synthesis — no external synth required

## Tech stack

- C++17
- JUCE
- CMake

## Build

JUCE is not vendored in this repository.

```bash
cd CBBWorkstation
cmake -S . -B build -DJUCE_SOURCE_DIR=/path/to/JUCE
cmake --build build
```

Alternatively point CMake at an installed JUCE package with `-DJUCE_DIR=/path/to/JUCE`,
or add a JUCE checkout as `CBBWorkstation/JUCE`. If JUCE is missing, CMake stops with
a clear error describing the expected setup.

## Documentation

- [docs/PROJECT_DEFINITION.md](docs/PROJECT_DEFINITION.md) — what it is, who it's for, the full feature list
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — implementation design (audio engine, sequencer, transposition, data model)
- [docs/MVP_SCOPE.md](docs/MVP_SCOPE.md) — current milestone scope
- [docs/WORKFLOW.md](docs/WORKFLOW.md) — user workflows
- [docs/DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md) — phased plan

## Status

Early development. The UI shell and project architecture are in place; the
real-time accompaniment engine is the current focus.

> A separate Python prototype for audio→chord import lives in `chordflow-analyzer/`.
> It is an optional, experimental component and not part of the core application.
