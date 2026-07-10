# Project Definition

## What ChordFlow Workstation Is

ChordFlow Workstation is a desktop **auto-accompaniment workstation** for creating
and playing styled backing arrangements from chord progressions. It brings the core
idea of an arranger keyboard — *give it chords, it plays you a band* — to a focused,
modern desktop application, and adds the tools to author the accompaniment styles
themselves.

The product has two halves that share one engine:

- **Play** — enter a chord progression, choose a style, and the app performs a full
  accompaniment that follows the chords, with live song-section control.
- **Create** — author and edit styles: the per-section drum/bass/chord/pad patterns
  and the voices that play them.

## Why It Exists

Turning chord ideas into something you can actually hear and play along with usually
means opening a full DAW, programming parts by hand, and assigning instruments. That
is slow and overkill when the goal is simply "play these chords in this groove."

Arranger keyboards solved this decades ago in hardware, but the workflow for *making*
the styles that power them lives in specialized, closed tools. ChordFlow Workstation
addresses both sides: a fast play experience for musicians, and a clear content
creation surface for the people who build styles.

## Target Users

**Performers & songwriters**
- guitarists, bassists, keyboard players, and hobbyists
- songwriters auditioning harmonic ideas with a real groove
- students practicing improvisation over changes

**Content designers**
- style/voice authors building reusable accompaniment content
- anyone designing grooves, section patterns, and instrument assignments

## Product Position

ChordFlow Workstation **is**:

- an auto-accompaniment workstation driven by chords and styles
- a live, section-based arranger for performance and practice
- a content creation tool for authoring styles and voices

ChordFlow Workstation **is not**:

- a full DAW or linear multitrack recorder
- a notation or scoring program
- an AI music generator

## What You Can Do (Feature List)

### Play

- Enter a chord progression as text or on the chord track
- Choose a style (genre groove) for the accompaniment
- Press play to hear drums, bass, chords, and pad perform the progression
- The accompaniment automatically transposes to follow each chord
- Trigger song sections live — Intro, Main A, Main B, Fill, Ending
- Adjust groove feel: tempo, swing, and energy
- Loop a section for practice
- Export the arranged result as a MIDI file

### Create

- Edit each track's pattern per section on a step grid
- Place drum hits and bass/chord/pad notes (relative to the chord)
- Assign a Voice (instrument sound) to each track
- Set per-track mix parameters: volume, pan, octave
- Save and load styles as reusable files

## MVP Intent

The first milestone proves the core promise end to end: a user can type chords,
pick a built-in style, press play, and hear a band that follows the progression —
then trigger a fill and an ending. Style editing and MIDI export round out the slice.
See [MVP_SCOPE.md](MVP_SCOPE.md).
