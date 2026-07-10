# Development Roadmap

Phased plan from the current UI shell to a demoable auto-accompaniment workstation.
Each phase ends at something runnable and showable.

## Phase 1 — Audible core

Make the instrument actually play.

- Build the Domain model: Style → Section → TrackPattern → PatternNote
- Stand up the audio engine: `AudioDeviceManager` + per-track `Synthesiser`
- Implement the sample-accurate PPQ sequencer clock
- Implement `resolvePitch` chord-following transposition
- Ship one built-in style (drums + bass + chord + pad)
- Wire transport: chord input → press play → hear a chord-following band

Milestone: type chords, press play, hear a band that follows them.

## Phase 2 — Arrangement & feel

Make it perform like an arranger.

- Section state machine with bar-quantized switching
- Intro, Main A/B, Fill (play-once → advance), Ending (play-once → stop)
- Tempo, swing, and energy affect the generated performance
- Per-track Voice selection and mix (volume, pan, octave)
- Loop and practice controls

Milestone: trigger sections live and shape the groove during playback.

## Phase 3 — Content creation

Make styles authorable.

- Step-grid pattern editor bound to the Domain model
- Edit drums (hits) and bass/chord/pad (relative-degree notes)
- Immediate audible feedback on edits
- Save / load styles to file

Milestone: author a new style and play it back.

## Phase 4 — Export & polish

Make it portable and presentable.

- MIDI export of the arranged result (reusing the live engine)
- Visual design pass toward the target UI skin
- Cross-platform build verification (macOS / Windows)
- README screenshots and a short demo capture

Milestone: a polished, cross-platform build with an exportable result and a clean demo.
