# ChordFlow Workstation

Transform chord progressions into practice-ready backing tracks.

ChordFlow Workstation is a JUCE-based desktop application for musicians who want to turn chord ideas into something playable without opening a full DAW. The product focuses on a fast workflow for entering chords, selecting a groove style, generating simple accompaniment, and practicing immediately.

## Motivation

Many tools can analyze songs and extract chord progressions:

`Audio File -> Chord Analysis -> Chord Progression`

The workflow often stops there. ChordFlow Workstation is built to bridge the gap between harmonic analysis and actual playing practice.

Typical user questions:

- What can I do with these chords now?
- How would these chords sound with a backing track?
- Can I practice improvisation over this progression right away?
- Can I try different groove styles without opening a DAW?

## Product Vision

ChordFlow Workstation is:

- a practice-focused accompaniment workstation
- a lightweight groove exploration tool
- a fast bridge from chord discovery to musical experimentation

ChordFlow Workstation is not:

- a full DAW
- a full production suite
- an AI composition product

## Target Users

Primary users:

- guitar players
- bass players
- beginner musicians
- hobbyists
- students learning improvisation
- musicians who find DAWs overwhelming

Secondary users:

- songwriters exploring harmonic ideas
- musicians experimenting with groove styles
- users interested in arranger-style workflows

## Core Workflow

`Input Chords -> Select Style -> Generate Accompaniment -> Practice -> Export MIDI`

Example:

`C - G - Am - F`

Choose a style such as `J-Pop`, `Ballad`, or `Blues`, generate a simple drum and bass backing, then practice guitar or bass over it.

## MVP Scope

The current MVP is focused on validating the workflow, not building a full arranger engine.

Included:

- manual chord progression input
- style selection
- section controls for `Main A`, `Fill`, and `Ending`
- groove controls for `Energy` and `Swing`
- transport controls for `Play`, `Stop`, and `Loop`
- basic accompaniment generation for drums and bass
- immediate playback feedback

Deferred until after MVP validation:

- advanced pattern authoring
- full arranger logic and transition rules
- recording
- piano roll or timeline editing
- plugin targets
- rich export workflows beyond basic MIDI output

## Tech Stack

- C++
- JUCE
- CMake

## Build Instructions

JUCE is not vendored in this repository yet.

Option 1:

- Add a JUCE checkout as `ChordFlowWorkstation/JUCE`

Option 2:

- Point CMake at an existing JUCE source checkout

```bash
cd CBBWorkstation
cmake -S . -B build -DJUCE_SOURCE_DIR=/Users/simjuheun/Developer/JUCE
cmake --build build
```

Option 3:

- Point CMake at an installed JUCE CMake package

```bash
cd CBBWorkstation
cmake -S . -B build -DJUCE_DIR=/path/to/JUCE
cmake --build build
```

If JUCE is missing, CMake stops with a clear error message describing the expected setup.
