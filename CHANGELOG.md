# Changelog

All notable changes to PyTheory are documented here.

## 0.13.1

- Fix drum pattern repeats: hits now correctly offset across cycles instead of piling up on the first bar

## 0.13.0

- Add drum synthesizer with 27 individual instrument voices (kick, snare, hat, conga, timbale, etc.)
- Add `play_pattern()` for playing drum patterns through the speakers
- Add `play_score()` for playing mixed drum patterns + chord progressions together
- Every `DrumSound` has a dedicated synthesis algorithm (pitch sweeps, noise bursts, membrane resonance, metallic rings)

## 0.12.0

- Add rhythm module: `Duration`, `TimeSignature`, `Note`, `Rest`, `Score`
- `Duration` enum with 8 note lengths (whole through sixteenth, dotted, triplet)
- `TimeSignature` with string parsing ("4/4", "3/4", "6/8", "12/8") and beats_per_measure
- `Score` class with fluent `.add()` / `.rest()` chaining, measure counting, and `save_midi()` export
- Measure-aware MIDI export with proper time signature and tempo meta events
- Add `DrumSound` enum with 27 General MIDI percussion sounds
- Add `Pattern` class with 48 drum pattern presets covering:
  - **Rock/Pop**: rock, half time, double time, disco, motown, train beat
  - **Jazz**: jazz, bebop, shuffle, linear, paradiddle
  - **Latin**: salsa, bossa nova, samba, cumbia, merengue, baiao, maracatu
  - **Afro-Cuban**: son clave 3-2/2-3, rumba clave 3-2/2-3, cascara, guaguanco, mozambique, nanigo, bembe, 6/8 afro-cuban, tresillo, habanera
  - **African**: afrobeat, highlife
  - **Caribbean**: reggae, dancehall
  - **Electronic**: house, trap, drum and bass, breakbeat
  - **Metal/Punk**: metal, blast beat, punk
  - **Other**: funk, hip hop, bo diddley, second line, new orleans, waltz, 12/8 blues
- `Pattern.to_score()` renders drum patterns to Score for MIDI export

## 0.11.0

- Add drop voicings: `Chord.close_voicing()`, `Chord.open_voicing()`, `Chord.drop2()`, `Chord.drop3()`
- Add `Key.modulation_path(target)` for chord-by-chord modulation suggestions via pivot chords
- Add `Scale.degree_name(n)` returning traditional names (tonic, dominant, leading tone, etc.)
- Add `Chord.extensions()` to suggest available 9th/11th/13th extensions
- Add `Tone.solfege` property for fixed-Do solfege syllables (Do, Re, Mi, Fi, etc.)
- Add CLI `identify` command for full chord analysis from a symbol
- Add CLI `midi` command for exporting progressions to Standard MIDI Files
- Expand documentation: solfege, Helmholtz, cents, slash chords, drop voicings, chord extensions, borrowed chord analysis, ADSR envelopes, MIDI export, new CLI commands

## 0.10.0

- Add `Scale.fitness()` to score how well a set of notes fits a scale (0.0–1.0)
- Add `Key.suggest_next(chord)` for chord progression suggestions based on functional harmony
- Add `Tone.helmholtz` and `Tone.scientific` properties for alternate pitch notation
- Add `Chord.slash(bass)` and `Chord.slash_name` for slash chord notation (C/G, Am/E)
- Add `save_midi()` for exporting tones, chords, and progressions as Standard MIDI Files
- Add chord tone highlighting in `Fretboard.scale_diagram()` — chord tones uppercase, passing tones lowercase
- Extend `Chord.analyze()` to recognize borrowed chords (bVI, bVII, bIII, etc.)

## 0.9.0

- Add ADSR envelope system with 8 presets: `Envelope.PIANO`, `ORGAN`, `PLUCK`, `PAD`, `STRINGS`, `BELL`, `STACCATO`, `NONE`
- Add `Chord.from_symbol()` parser — handles any standard chord symbol (e.g. "F#m7b5", "Bbmaj9", "Gsus4") without lookup tables
- Add `Key.pivot_chords(target)` for finding modulation pivot chords between two keys
- Add `Scale.parallel_modes()` to show all modes sharing the same notes (C major → D dorian, E phrygian, etc.)
- Add `Tone.cents_difference(other)` for measuring fine pitch differences in cents
- Add `--envelope` flag to CLI play command
- CLI play command now uses `Chord.from_symbol()` for broader chord parsing
- Replace hardcoded `c_index = 3` with named `C_INDEX` constant throughout

## 0.8.3

- Add `Chord.symbol` property for standard shorthand notation (Cmaj7, Dm, G7, m7b5, etc.)
- Add `Key.common_progressions()` to realize all named progressions in a key
- Add CLI commands: `modes`, `circle`, `progressions`

## 0.8.2

- Use flat spellings in CHARTS `acceptable_tone_names` (e.g. Bbm now shows Bb/Db/F instead of A#/C#/F)

## 0.8.1

- Use musically correct flat spellings in flat keys (F major gives Bb, not A#)

## 0.8.0

- Add `Fretboard.scale_diagram()` for visual scale layouts on any instrument
- Add `play_progression()` for sequential chord playback with gaps
- Add cookbook documentation page with practical recipes
- Curated guitar fingering overrides for common open chords
- Fingering memoization with bounded cache, barre detection, 4-fret span constraint
- API ergonomics: `Fretboard.chord()`, convenience constructors, slow test markers

## 0.7.0

- Add `Fretboard.chord()` method for named chord lookups
- Improve fingering algorithm with better voicing selection
- Rewrite all documentation in REPL style with verified output

## 0.6.1

- Fix sawtooth and triangle wave generation
- Add WAV export via `save()`
- Add CLI tests and play module tests
- Skip play module tests when PortAudio is not available

## 0.6.0

- Support flat note names (Db, Bb, Eb, etc.) throughout the system
- Add `Fingering` class for labeled chord fingerings
- Add `pytheory play` CLI command for playing notes and chords
- Add 12 example scripts showcasing pytheory features
- Expand documentation with undocumented features and CLI guide

## 0.4.1

- Add `--temperament` flag to CLI tone command
- Add Symbolic Pitch section to tones docs

## 0.4.0

- Add key signatures, scale diagrams, chord building, and progression analysis
- Add CLI tool (`pytheory tone`, `pytheory chord`, `pytheory key`, etc.)
- Add Jupyter notebook tutorial
- Improve test coverage from 93% to 97% (476 tests)
- Add type hints, docstrings, and property caching throughout

## 0.3.2

- Add type hints and docstrings throughout the library

## 0.3.1

- Add capo support, chord merging (`+`), tritone substitution
- Add secondary dominants, Nashville number system
- Add more common progressions (blues, jazz, flamenco, modal)

## 0.3.0

- Add interval naming (`Tone.interval_to()`)
- Add MIDI conversion (`Tone.midi`, `Tone.from_midi()`)
- Add `Tone.from_frequency()`, `Tone.transpose()`
- Add `Chord.root`, `Chord.quality` properties
- Add `Chord.from_name()`, `Chord.from_intervals()`, `Chord.from_midi_message()`
- Add `Interval` constants (MINOR_THIRD, PERFECT_FIFTH, etc.)
- Add `PROGRESSIONS` dict with common named progressions
- Add `Tone.enharmonic` property
- Add inversions, harmonize, and Roman numeral progressions
- Add `Key` class with detection, signatures, relative/parallel keys
- Add `Scale.detect()` and `Chord.from_tones()` convenience constructors
- Add 25 instrument presets (mandolin family, violin family, banjo, harp, world instruments, keyboard)
- Add `Tone.circle_of_fifths()` and `Tone.circle_of_fourths()`
- Add chord identification (17 types), voice leading, tension scoring
- Add beat frequencies, Plomp-Levelt dissonance model, harmony scoring

## 0.2.0

- Add `Fretboard` class for guitar fretboards
- Add `play()` function with sine, sawtooth, and triangle wave synthesis
- Add chord harmony and dissonance calculations
- Modernize project structure (pyproject.toml, sounddevice)

## 0.1.0

- Initial release
- Western 12-tone system with tones, scales, and basic chord support
- Temperament support (equal, Pythagorean, meantone)
- Indian (Hindustani), Arabic, Japanese, Blues, and Gamelan systems
