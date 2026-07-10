# MVP Scope

The MVP is a single vertical slice that proves the core promise end to end:
**type chords, pick a style, press play, hear a band that follows the progression,
and shape the arrangement live.**

## Included

- Standalone JUCE desktop application (macOS first, Windows-ready)
- Manual chord progression input (text) with a visible chord track
- 2–3 built-in styles, each with drums / bass / chord / pad tracks
- Real-time audio playback via built-in synthesis (no external synth needed)
- Chord-following transposition so the accompaniment tracks each chord
- Live arranger sections: Intro, Main A, Main B, Fill, Ending (bar-quantized)
- Transport: play, stop, loop; tempo and swing controls
- Per-track Voice selection and basic mix (volume, pan, octave)
- A step-grid pattern editor for one track type as a first authoring surface
- MIDI export of the arranged result
- Updated product and architecture documentation

## Excluded (for now)

- Large built-in style library
- Full multi-track pattern editing with deep per-note editing
- Recording / linear arrangement timeline
- Audio (non-MIDI) tracks and effects processing
- Notation / score view
- Plugin (VST/AU) build targets
- Audio→chord import (the parked `chordflow-analyzer` prototype)

## Success Criteria

- The app builds and runs as a standalone JUCE application
- A reviewer with no explanation understands it is an auto-accompaniment tool
- This demo flows without a hitch:
  1. enter a chord progression
  2. choose a style
  3. press play and hear a full, chord-following band
  4. trigger a Fill, then an Ending
  5. edit a pattern and hear the change
  6. export a `.mid`
- The code is cleanly layered (Domain / Engine / Audio / UI) and easy to extend
