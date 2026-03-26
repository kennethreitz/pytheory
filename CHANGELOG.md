# Changelog

All notable changes to PyTheory are documented here.

## 0.25.6

- Swing now applies to drum hits — offbeats shift with the groove, everything locks into the same pocket
- Improved snare: 220Hz body, transient click, tanh saturation
- Improved hi-hats: metallic harmonics (6k+8.5k+12k Hz), crisper attack, shorter decay

## 0.25.5

- Improved snare: 220Hz body, transient click, tanh saturation — snappier and more present
- Improved hi-hats: metallic harmonics (6k+8.5k+12k Hz), shorter decay, crisper attack

## 0.25.4

- Add master bus compressor/limiter — louder, punchier, more cohesive mixes
- Feed-forward compression with configurable threshold, ratio, attack, release
- Makeup gain restores loudness after compression
- Brick-wall limiter at 0.95 prevents clipping
- Replaces simple normalization in render_score()

## 0.25.3

- Add `pytheory repl` — interactive music theory scratchpad and composition tool
- Context-aware prompt shows key, bpm, drums, active part + effects
- Theory commands: key, chords, modes, scales, circle, interval, identify, system
- Composition: drums, part, add, rest, arp, prog, effects, automation, LFO
- Guitar: fingering, scale diagram
- 6 musical systems with correct default tonics
- REPL guide documentation

## 0.25.1

- Add `pytheory demo` CLI command — plays a randomly generated track, different every time
- Rewrite README to showcase the full feature set (composition, effects, drums, MIDI export)

## 0.25.0

- Add sidechain compression — kick ducks pad/bass for the classic EDM pump effect
- Add song structure: `score.section("verse")`, `score.section("chorus")`, `score.repeat("verse")`
- Punchier kick drum: 808-style with faster pitch sweep (200→45Hz), sub thump, and soft saturation
- Section repeat copies all part notes, drum hits, and automation with proper offset

## 0.24.1

- Add `humanize` parameter on Parts — random micro-timing and velocity variation
- Makes programmed parts feel like a real player (0.1 = subtle, 0.3 = natural, 0.5+ = loose)

## 0.24.0

- Add per-note velocity: `lead.add("C5", Duration.QUARTER, velocity=90)` — dynamics, accents, ghost notes
- Add swing/groove: `Score("4/4", bpm=120, swing=0.5)` — shuffles every other note for human feel
- Add tempo changes mid-song: `score.set_tempo(140)` — accelerando, ritardando, tempo drops
- Add `Part.fade_in(bars)` and `Part.fade_out(bars)` — volume envelopes over sections
- Arpeggiator supports velocity parameter
- Per-part swing override (set independently from score swing)
- Tempo map engine: beat-to-sample conversion handles variable BPM throughout a score

## 0.23.0

- Add convolution reverb with 7 synthetic impulse responses: Taj Mahal, cathedral, plate, spring, cave, parking garage, canyon
- Each IR models real acoustic properties: early reflections, frequency-dependent absorption, diffusion density, and modulation
- FFT-based convolution via `scipy.signal.fftconvolve` for fast processing even with long tails (12s Taj Mahal)
- Select via `reverb_type` parameter on `Score.part()` — drop-in alongside existing algorithmic reverb
- IR cache for zero-cost reuse across parts
- Automatable via `Part.set(reverb_type="cathedral")` mid-song

## 0.22.0

- Add `Part.lfo()` for automated parameter modulation (filter sweeps, tremolo, auto-wah)
- 4 LFO shapes: sine, triangle, saw, square
- Configurable rate (cycles per bar), min/max range, duration, and resolution
- Stack multiple LFOs on different parameters for complex modulation

## 0.21.0

- Add `Part.set()` for mid-song effect automation (filter sweeps, reverb swells, distortion kicks)
- Add chorus effect (LFO-modulated delay, Juno-style)
- Renderer segments audio at automation points for per-section effect processing
- Updated effect chain: distortion → chorus → lowpass → delay → reverb
- Document automation, chorus, and updated signal chain

## 0.20.0

- Add `Part.arpeggio()` — arpeggiator with up/down/updown/downup/random patterns, octave spanning
- Fix Roman numeral parser to handle flat/sharp degree prefixes (bVI, bVII, bIII, #IV)
- Add `song_showoff.py` — generative composition that's different every time, uses every feature
- 4 mood palettes (dark, bright, ethereal, aggressive) with matched keys, progressions, drums, and effects

## 0.19.1

- Add `Part.arpeggio()` — arpeggiator with up/down/updown/downup/random patterns, octave spanning, and division control
- Arpeggiator chains with legato + glide for classic acid/trance sequencer sound
- Rename rhythm docs to "Sequencing: Rhythm and Scores"
- Document arpeggiator, legato, and glide in rhythm guide

## 0.19.0

- Add legato mode for parts — continuous waveform without retriggering envelope per note
- Add glide/portamento — smooth pitch slides between consecutive notes (303-style)
- Legato renders entire phrase as one oscillator with phase-accumulating frequency changes
- Glide uses exponential interpolation for perceptually linear pitch slides

## 0.18.1

- Add distortion effect (tanh soft-clip waveshaping) with drive and mix controls
- 3 new example songs: Dub Delay Madness (separate delay snare), Liquid DnB (174bpm), Late Night Texts (Drake-style trap)
- 16 total songs in the song player

## 0.18.0

- Add per-part audio effects: reverb, delay, and lowpass filter
- Reverb: Schroeder algorithm with configurable mix and decay
- Delay: tempo-synced echoes with feedback control
- Lowpass: 12 dB/octave biquad filter with resonance (Q) control
- All effects set at part creation: `score.part("lead", reverb=0.3, delay=0.25, lowpass=2000, lowpass_q=1.5)`
- Effects applied per-part before mixing for independent processing

## 0.17.0

- Add 10 new groove presets: country, ska, dub, jungle, techno, gospel, swing, bolero, tango, flamenco (58 total)
- Add 10 new fill presets: reggae, afrobeat, bossa nova, house, trap, hip hop, disco, cumbia, highlife, second line (21 total)
- Every major genre family now has matching groove + fill presets

## 0.16.0

- Add drum fill system with 11 genre-specific presets: rock, rock crash, jazz, jazz brush, salsa, samba, funk, metal, blast, buildup, breakdown
- `Pattern.fill("rock")` returns a 1-bar fill pattern
- `Score.fill("rock")` inserts a fill at the current position
- `Score.drums("rock", repeats=8, fill="rock", fill_every=4)` auto-fills every Nth bar
- Without `fill_every`, fill replaces only the last bar

## 0.15.1

- Add `Synth.PWM_SLOW` and `Synth.PWM_FAST` — pulse width modulation with LFO sweep (Juno-style pads)
- Add `Score.drums()` shorthand for `score.add_pattern(Pattern.preset(...), repeats=...)`
- Update all docs to use `score.drums()` syntax and document all 10 synth waveforms

## 0.15.0

- Add 5 new synth waveforms: `Synth.SQUARE`, `Synth.PULSE`, `Synth.FM`, `Synth.NOISE`, `Synth.SUPERSAW`
- Square wave: classic chiptune / 8-bit sound (odd harmonics at 1/n)
- Pulse wave: variable duty cycle for NES-style timbres (25%, 12.5%)
- FM synthesis: DX7-style frequency modulation (electric piano, bells, brass, metallic)
- Noise: white noise for percussion textures and effects
- Supersaw: 7 detuned saw oscillators for trance/EDM pads
- All 8 synths available in both the API (`Synth.FM`) and Part strings (`synth="fm"`)
- CLI play command supports all 8 waveforms

## 0.14.0

- Add `Part` class for multi-voice Score arrangements (lead, bass, pads, etc.)
- `Score.part()` creates named parts with independent synth, envelope, and volume
- `Score.add_pattern()` for attaching drum patterns
- `render_score()` exported for headless buffer rendering
- Parts accept raw float beat values alongside `Duration` enums
- All 10 example songs rewritten with drums + chords + lead + bass parts

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
