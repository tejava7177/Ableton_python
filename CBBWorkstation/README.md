# C.B.B Workstation

C.B.B Workstation is a JUCE-based standalone desktop application prototype for beginner musicians who want an approachable accompaniment workstation. The MVP focuses on a simple practice workflow built around chord entry, style selection, section switching, groove shaping, and transport control.

## MVP Goal

Validate this workflow with a clean desktop UI skeleton:

`App launch -> chord progression input -> style selection -> section switching -> groove adjustment -> playback/practice`

This version does not implement full MIDI playback yet. It establishes project structure, domain scaffolding, engine placeholders, and a workstation-style control surface.

## Tech Stack

- C++
- JUCE
- CMake

## Build Instructions

JUCE is not vendored in this repository yet.

Option 1:
- Add a JUCE checkout as `CBBWorkstation/JUCE`

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

## Current MVP Surface

- Chord progression input
- Style selection
- Section buttons: Main A / Fill / Ending
- Groove controls: Energy / Swing
- Transport controls: Play / Stop
- Status display

## Not Included Yet

- Real MIDI playback
- Style pattern generation
- Audio recording
- Piano roll editing
- Plugin/VST targets
- Yamaha proprietary formats
