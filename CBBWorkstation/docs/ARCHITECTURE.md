# Architecture & Implementation Design

This document describes how ChordFlow Workstation is built: the data model, the
real-time audio engine, the chord-following transposition that makes the
accompaniment track the progression, and how the pieces map onto the codebase.

## Layered overview

```
UI            JUCE Components — chord input, style/section panel,
              pattern grid editor, voice/mix inspector, transport

Engine        Sequencer clock, arrangement state machine, chord-following
              transposition, MIDI export

Audio         AudioDeviceManager + per-track Synthesiser voices

Domain        Pure data: Chord, Style, Section, Pattern, PatternNote, Voice
```

The current repository already separates `Source/Domain`, `Source/Engine`, and
`Source/UI`. Today the `Engine` layer is a placeholder (`PatternGenerator` returns
descriptive strings, `MidiPlaybackEngine` only tracks state); this design replaces
those stubs with a working real-time engine.

## Domain data model

A **Style** is the unit of accompaniment content.

```
Style
 ├─ name, default tempo, time signature
 └─ Section[]            // Intro, MainA, MainB, Fill, Ending
      └─ TrackPattern[]  // one per track: Drums, Bass, Chord, Pad
           ├─ Voice      // assigned instrument sound + mix params
           └─ PatternNote[]
                ├─ step / position   (within the pattern, in ticks or steps)
                ├─ pitch             (see "relative vs absolute" below)
                ├─ velocity
                └─ length
```

### Relative vs absolute pitch (the key idea)

- **Drums** use absolute MIDI notes from the General MIDI drum map
  (36 = kick, 38 = snare, 42 = closed hat, …). They never transpose.
- **Bass / Chord / Pad** store pitch as a value **relative to the current chord**,
  not an absolute note — e.g. "root", "third", "fifth", or a scale degree. This is
  what lets one pattern voice any chord.

## Chord-following transposition

The arranger magic is one function:

```cpp
int resolvePitch(const PatternNote& note, const Chord& current) const;
```

Given the current chord (root pitch class + chord type → its chord tones) and a
note stored as a relative degree, it returns the absolute MIDI note to play. As the
transport advances over the chord track, `current` changes per bar (or per chord
event), so the same stored pattern is re-voiced automatically. A bass note stored as
"root" plays A under Am and G under G; a chord pattern stored as tones {1,3,5} voices
A-C-E under Am and C-E-G under C.

## Real-time sequencer clock

Timing is driven from the audio callback for sample accuracy.

- Maintain a transport position in **PPQ** (pulses per quarter note).
- Each audio block of `numSamples` at `sampleRate` and tempo `bpm` advances PPQ by
  `numSamples / sampleRate * (bpm / 60)`.
- For each track, find the pattern events whose positions fall inside the block's
  PPQ window, resolve their pitch against the current chord, and emit them as
  `juce::MidiMessage` note-ons/offs into a per-track `juce::MidiBuffer` with
  sample-offset timing.
- Patterns loop within the active section; section length defines the loop point.

```
audio callback ──advance PPQ──▶ collect due events ──resolvePitch──▶ MidiBuffer
                                                                       │
                                                       Synthesiser.renderNextBlock
                                                                       ▼
                                                                  audio output
```

## Audio engine (self-contained sound)

Each track owns a `juce::Synthesiser`:

- **Drums** — a `Synthesiser` whose `SamplerSound`s map drum samples to GM notes
  (or short synthesized hits to avoid bundling samples initially).
- **Bass / Pad** — `SynthesiserVoice`s with simple subtractive synthesis.
- **Chord** — a polyphonic synth voice.

A `juce::AudioDeviceManager` drives an `AudioIODeviceCallback` that renders every
track's synth into the output buffer. Building sound in-app means the demo is
audible with no external synth or DAW — a requirement for a standalone instrument.

An optional `juce::MidiOutput` path can additionally send the same events to an
external synth, demonstrating the MIDI protocol side.

## Arrangement state machine

Section control mirrors a hardware arranger:

- Holds `currentSection` and an optional `queuedSection`.
- Pressing a section (e.g. **Fill**) queues it; the switch is **quantized to the next
  bar boundary** so it stays musical.
- A **Fill** plays once, then advances to its queued main section.
- **Ending** plays once, then stops the transport.

## Voice & mix

Each `TrackPattern` carries a `Voice`: the chosen instrument sound plus volume, pan,
and octave. Volume/pan apply as gain on the track's rendered audio; changing the
Voice swaps the synth's sound. These map directly to the "Voice Parameter" content
type the product targets.

## Pattern editor (content creation)

The step grid is a custom `juce::Component`:

- Renders tracks × steps; reads/writes the active `Section`'s `TrackPattern`s.
- Clicking a cell toggles a step (drums) or sets a note/degree (bass/chord/pad).
- Edits mutate the Domain model in place, so the next loop plays the change —
  immediate audible feedback while authoring.

Styles serialize to a simple file (JSON or JUCE `ValueTree`/XML) for save and load.

## MIDI export

To export, the engine walks the arrangement across the chord progression, resolves
every pattern note to an absolute, timestamped MIDI event, writes them into a
`juce::MidiFile` (one track per part), and saves a `.mid`. This reuses the same
`resolvePitch` and clock logic as live playback, so exported output matches what was
heard.

## Mapping to the current code

| Area | Today | Target |
| --- | --- | --- |
| `Domain/Style.h`, `Section.h`, `Chord.h` | enums / minimal | full Style→Section→Pattern→Note model |
| `Engine/PatternGenerator.h` | returns description strings | builds/edits real patterns |
| `Engine/MidiPlaybackEngine.h` | state flags only | real-time clock + synth playback |
| `Engine/ChordParser.h` | parses chord text | reused as-is, feeds the chord track |
| `UI/*` | static panels | wired to the engine + pattern editor |
| audio output | none | `AudioDeviceManager` + per-track `Synthesiser` |
