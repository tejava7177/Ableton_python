# MVP Scope

## Included

- Standalone JUCE desktop application target
- CMake-based project setup
- Modular UI component structure
- Chord progression text input
- Style selection control
- Section buttons for Main A, Fill, Ending
- Groove controls for Energy and Swing
- Transport controls for Play, Stop, and Loop
- Status label for immediate user feedback
- Chord parsing and validation scaffolding
- Simple accompaniment generation for drums and bass
- Playback engine scaffolding that can support immediate practice feedback
- Basic MIDI export planning in the architecture
- Documentation for product definition and workflow

## Excluded

- Advanced arranger generation
- Rich section transition rules
- Editable pattern authoring tools
- Pattern library authoring tools
- Recording
- DAW editing workflows
- Piano roll or timeline editing
- Plugin build targets
- Proprietary file format integration
- Full production-oriented export workflows

## MVP Success Criteria

- The project opens as a standalone JUCE app when JUCE is available
- A user can understand the chord-to-backing workflow without explanation
- The first accompaniment pass is good enough for basic practice and groove comparison
- The codebase is clean enough to extend into stronger playback, generation, and export work
