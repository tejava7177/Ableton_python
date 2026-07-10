# Workflows

ChordFlow Workstation supports two workflows that share one engine: playing an
arrangement, and creating the style that drives it.

## Play workflow

1. Launch the app
2. Enter a chord progression (text or chord track)
3. Choose a style
4. Press play — drums, bass, chords, and pad perform the progression
5. Trigger sections live: Intro → Main A / Main B, drop a Fill, end with Ending
6. Shape the feel with tempo, swing, and energy; loop a section to practice
7. Adjust per-track Voice and mix as desired
8. Export the result as a MIDI file

The accompaniment always follows the chord track: every pattern note is voiced
against the current chord, so changing the progression instantly changes what plays.

## Create workflow (style authoring)

1. Choose or start a style
2. Select a section to edit (Intro, Main A, Main B, Fill, Ending)
3. Edit each track's pattern on the step grid:
   - drums: toggle hits per step
   - bass / chord / pad: place notes as degrees relative to the chord
4. Assign a Voice to each track and set volume, pan, and octave
5. Audition against a test progression — edits play back immediately
6. Save the style as a reusable file

## UX intent

The interface should read as a compact, performance-ready instrument rather than a
DAW: a few large, legible controls that imply musical action. Playing should feel
immediate; authoring should feel like sketching patterns, not engineering them.

## Design reference

The target main screen layout — transport + key/tempo, arranger sections, the
track × step pattern grid, the Voice inspector, and the chord track — is captured in
the project's UI mockups and informs the JUCE component layout.
