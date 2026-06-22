# Changelog

All notable changes to PyTheory are documented here.

## 0.57.4

Notation export fidelity — the held-note and articulation gaps surfaced
in 0.57.3.

- **`Part.hold()` notes no longer corrupt bar lengths in notation.** A
  held (overlapping) note was emitted at full duration *and* advanced the
  bar counter, so every following barline drifted out of place in ABC,
  LilyPond, and MusicXML. Held notes are now folded into the next sounding
  note as a chord — the pitch is kept and bars stay aligned. (Single-voice
  notation can't show the exact sustain; use MIDI export for that.)
- **Articulations now reach the page.** `staccato`, `accent`, `marcato`,
  `tenuto`, and `fermata` are emitted as LilyPond marks (`-.`, `->`, `-^`,
  `--`, `\fermata`) and MusicXML `<articulations>`/`<fermata>` elements.
  MusicXML had been extracting the articulation and then discarding it.

Still not represented in notation export (a single-voice limitation, not
a regression): lyrics and per-note velocity.

## 0.57.3

Two more silent-data-loss holes of the same kind as 0.57.2, found by
auditing the export/render surface.

- **Drums no longer vanish from exported MIDI after `drums(split=True)`.**
  Splitting moves drum hits out of the `drums` part into per-instrument
  group parts (`kick`/`snare`/`hats`); `save_midi()` was reading only the
  now-empty default proxy, so a split score exported with no drums at all
  (while `render_score()` still played them — a render-vs-export
  asymmetry). Export now gathers hits from every part.
- **A part with both melodic notes and drum hits no longer loses its
  notes.** A part counts as "drums" if it has any hits, and the renderer
  skipped such parts entirely — silently dropping the melodic notes from
  the audio. Only purely-percussion parts are skipped now.

## 0.57.2

MIDI round-trip correctness, a new analysis command, and more polish.

- **MIDI round-trip actually works now.** Two coupled bugs are fixed:
  `save_midi()` only ever wrote the default part (plus drums), so a
  multi-part score — the normal way to compose — exported nearly empty;
  it now merges every part onto its own MIDI channel into one track. And
  `from_midi()` flattened simultaneous notes into a sequence, turning
  imported chords into arpeggios; it now groups same-onset notes into
  `Chord`s, so a C triad imports as a chord. Sequential melodies are left
  alone.
- **`pytheory analyze song.mid`.** The `analyze` command now accepts a
  MIDI file (a lone `.mid`/`.midi` argument): it detects the key and
  prints a chord timeline with Roman-numeral analysis, text or `--json`.
  It reads raw MIDI events, so it sees true vertical harmony regardless
  of the import grouping above.
- **`Score.repeat()` keeps every note property.** Repeating a section
  used to silently drop pitch bends, articulations, lyrics, and hold
  flags — it now copies the whole note.
- **Chords are comparable and hashable.** `Chord` gains `__eq__`/`__hash__`
  (by voicing), so chords work in sets and as dict keys, and `c1 == c2`
  compares notes instead of identity.
- **Clearer "needs a system" errors.** The three tone methods that need a
  tuning system (index, interval math, pitch) now share one explicit
  guard with a helpful message instead of catching a bare
  ``AttributeError`` — and ``Tone.from_string(system=None)`` documents
  that it skips validation.

## 0.57.1

A quality/DX polish sweep — robustness fixes and friendlier errors, no
behavior changes to correct output.

- **`Key.secondary_dominant()` no longer crashes on out-of-range
  degrees.** Degrees past the octave now wrap (V/9 == V/2) and a
  non-positive degree raises a clear `ValueError` instead of an
  `IndexError`.
- **Malformed MIDI is handled.** `Score.from_midi()` guarded against a
  zero tempo (would divide-by-zero; now falls back to 120 BPM) and a
  zero/negative `ticks_per_beat` (now raises a clear error).
- **Friendlier errors.** `Fretboard.chord()` raises a descriptive
  `ValueError` (not a bare `KeyError`) when a symbol can't be parsed or
  voiced; `Scale[...]` and the scale registry explain what was expected
  and list what's available; `TimeSignature.from_string()` explains the
  expected `'beats/unit'` format.
- **`TimeSignature` is hashable again.** It defined `__eq__` without
  `__hash__`, making it unusable as a dict key or set member; added
  `__hash__`.
- **Two more audit follow-ups.** `nashville("b7")` (and other flat degrees)
  used to crash trying to `int("b")` — it now reads a leading `b`/`#` as a
  borrowed degree (`"b7"` → ♭VII = B♭ major), alongside the diatonic and
  `"m"` cases. And `Chord.analyze()` gains `secondary_dominants=True`, which
  labels applied dominants as `"V7/V"` instead of the bare `"II7"` — the
  inverse of `progression("V7/V")`, so generate→analyze round-trips.
- **Docs & types.** Added docstrings to `Tone.pitch()` and
  `Scale.degree()`, and a type hint to `Chord.negative_harmony(key=...)`.

## 0.57.0

A correctness pass — an adversarial audit of the theory engine found 23
real bugs, and this release fixes all of them. The headline ones change
output you may have seen before, so they're worth reading.

- **Flat-key guitar chords are no longer broken.** The fretboard voicer
  matched chord tones by spelled name, so a fretboard `D#` never matched
  a chord's `Eb` — and roughly sixty flat-key chords (every Eb/Ab/Db/Gb
  voicing, plus Fm/Cm) silently came out as broken two-string fragments
  that didn't even contain all their notes. Matching is now by pitch
  class, so `Fretboard.guitar().chord("Eb")` returns a real, complete
  voicing.
- **Maqam Saba has its diminished 4th back.** The module advertises Saba's
  "unmistakable diminished 4th," then encoded a major 3rd in that exact
  slot — a heptatonic scale with two adjacent thirds and no 4th degree.
  Saba is now `Do Re↓ Mib Fab Sol Lab Sib`, with the `Fab` tuned to a
  32/25 (≈427¢) just diminished fourth.
- **Extreme keys spell correctly.** Gb major now reads `Gb Ab Bb Cb Db
  Eb F` (not `…B…`), F# major uses `E#`, C# major uses `B#`, Cb major
  uses `Fb` — one letter per degree, every time, with the right key
  signature. Octave-transposed chord tones keep their spelling too (the
  IV chord in Eb is `Ab C Eb`, not `Ab C D#`).
- **Accidental Roman numerals are chromatic.** `bVII`/`bVI`/`bIII` are now
  measured from the parallel major, so the Mixolydian/rock `bVII` is `Bb`
  in C minor — not the doubly-flattened `A` you got before. Bare diatonic
  numerals are unchanged.
- **`from_symbol` no longer swallows what it doesn't understand.** `C7b9`
  used to silently parse as a plain `C7`, and `Cmajgarbage` as `C major`.
  Both now raise. Real suspended dominants (`E7sus4`, `C7sus2`) are
  supported, 6th chords identify as themselves (`C6`, not `Am7`), and a
  13th chord drops the avoid-note 11th so it voices cleanly.
- **Threaded rendering is deterministic again.** The ensemble renderer
  reseeded the *global* RNG mid-render, corrupting humanize/analog
  determinism of every other part and breaking `render_scores()` under
  threads. It now uses an isolated per-voice RNG. The sub-oscillator +
  detune combination also no longer leaks the octave-below sub into the
  main voice at full gain.
- **Friendlier edges.** SVG diagrams no longer crash on chords that don't
  identify; the CLI prints a one-line error instead of a traceback on bad
  input (set `PYTHEORY_DEBUG=1` to see the stack); `play()`/`save()` point
  you to `play_score()`/`save_midi()` when handed a `Score`; garbage Roman
  numerals are rejected; Nashville `m` actually forces minor;
  `negative_harmony` spells with flats to match its scale; `Tone.from_midi()`
  round-trips through octave -1; and `Tone.from_midi(..., prefer_flats=True)`
  is now available.

## 0.56.0

- **Arabic maqamat — `pytheory.Maqam` and `pytheory maqam`.** What the
  `Raga` class does for Hindustani music, this does for Arabic: ten of
  the best-known maqamat (Rast, Bayati, Hijaz, Nahawand, Kurd, Ajam,
  Hijazkar, Saba, Suznak, Nakriz) with their scale degrees, the **ajnas**
  they're built from, their **seyir**, and — the whole point — their real
  **quarter-tone (just) intonation**. The neutral 2nds, 3rds, 6ths and
  7ths (the half-flats a piano can't play) render where they actually
  sit: Rast's neutral third is a 27/22, ~45 cents under the tempered E.
  `Maqam.get("rast")`, `Maqam.by_family("hijaz")`; `.degree_names()`,
  `.note_names(tonic)` (nearest 12-TET), `.maqam_table(tonic)` (ratio +
  cents off 12-TET), `.just_frequencies(tonic)`, and `.play(tonic)` (oud,
  movable tonic). CLI: `pytheory maqam rast --tuning --play`.

## 0.55.0

- **Chord diagrams for any chord.** `Fretboard.chord()` and
  `tab_image()` no longer stop at the ~144 charted voicings — any symbol
  `Chord.from_symbol` can parse (`F#m7b5`, `Csus2`, `Gadd9`, `Aaug`,
  `Cdim7`, …) now gets a voicing computed from its notes, by searching
  the neck and scoring hand positions for completeness, span, open
  strings, root-in-bass, and barre/finger economy. Charted chords keep
  their curated shape. New `diagrams` extra (`cairosvg`) for PNG export.
- **Carnatic ragas.** 18 of the best-known Carnatic ragas join the 36
  Hindustani ones (36 → 54) — Shankarabharanam, Kalyani, Kharaharapriya,
  Hanumatodi, Mayamalavagowla, Mohanam, Hindolam, Charukesi, Keeravani,
  Kambhoji, Madhyamavati, and more — each with its parent melakarta. New
  `Raga.tradition` attribute, `Raga.by_tradition()`, and `pytheory raga
  --tradition hindustani|carnatic`.
- **Parallel batch rendering — `render_scores()`.** A single
  `render_score` is already fast, so the multicore win is in batch work:
  exporting an album, rendering many clips, serving several requests.
  `render_scores(scores, workers=)` renders each Score on its own thread
  (NumPy releases the GIL during the math), about 2x on a typical
  machine, with no change to how any individual Score sounds.

## 0.54.1

- **Correct Roman-numeral progressions in the published package.** The
  case-sensitive `progression()` parser and the expanded `PROGRESSIONS`
  set (14 → 34) from the 0.54.0 work are now on PyPI: lowercase numerals
  build minor chords (so the Andalusian cadence keeps its minor v and the
  Mixolydian vamp its major-ish vii), `"bVII"`/altered degrees transpose
  to the correct borrowed triad, and secondary-dominant slash notation
  (`"V7/V"`, `"vii°/ii"`) parses. These landed just after 0.54.0 was
  uploaded, so `pip install -U pytheory` now matches the documented
  0.54.0 behaviour.

## 0.54.0

- **Roman-numeral progressions now mean what they say.** `progression()`
  reads the numeral's **case** for quality (so an uppercase `"V"` in a minor
  key gives the harmonic-minor *major* dominant, and `"IV"` gives the
  Dorian major-IV), honours quality markers (`"°"`, `"ø"`, `"+"`, `"maj"`),
  and builds **flat/sharp degrees** as the correct borrowed chord (`"bVII"`
  → a B♭ major triad, not a clipped diminished one), and parses
  **secondary dominants** with slash notation (`"V7/V"`, `"vii°/ii"`).
  Previously it ignored case and mis-transposed altered degrees, so
  modal/minor progressions rendered wrong — the Andalusian cadence ended on
  a minor v, the Mixolydian vamp on a diminished vii°, and minor ii–V–i got
  a minor v7. *(Behaviour change: lowercase numerals now build minor chords
  even in a major key.)*
- **More built-in progressions (14 -> 34).** `PROGRESSIONS` gains 20 named
  progressions across pop, blues (quick-change, 8-bar, minor 12-bar), jazz
  (extended turnarounds, minor ii-V-i, ragtime and the rhythm-changes bridge
  built from secondary dominants), classical (the circle of fifths,
  Pachelbel variant), and a range of minor and modal loops.
- **Reharmonization.** `reharmonize(chord, key)` suggests substitution
  ideas for a chord — tritone sub (for dominants), diatonic swaps sharing
  two or more notes, the secondary dominant that tonicises it, and its
  negative-harmony mirror — each with a technique name and description.
  `reharmonize_progression(chords, key, technique=…)` reworks a whole
  progression — `"secondary_dominants"` (the cycle-of-dominants insertion),
  `"tritone"`, or `"diatonic"`. Both are reachable from
  `pytheory reharmonize` (one chord → ideas, several → a reharmonized
  progression), with `--json` / `--play`.
- **`--json` and `--play` across the CLI.** The theory commands (`tone`,
  `scale`, `chord`, `key`, `progression`, `identify`, `analyze`, `detect`,
  `modes`, `circle`, `fingering`) gain `--json` for structured, pipeable
  output and `--play` to hear the result (the note/chord/scale/progression).
- **`pytheory analyze` CLI command.** Hand it a chord progression and it
  prints the harmony: the auto-detected key (or pass `--key`/`--mode`),
  each chord's Roman numeral with secondary dominants labelled, and the
  cadences — surfacing the whole analysis layer from the terminal.
  `pytheory analyze C D7 G7 C`.
- **Secondary-dominant detection.** `detect_secondary_dominant(chord, key)`
  labels applied dominants — `D7` in C is `V7/V`, `E7` is `V7/vi` — the
  analytical inverse of the existing `Key.secondary_dominant(degree)`
  builder. `analyze_progression(..., secondary_dominants=True)` uses those
  labels in context instead of the bare scale degree (`II7`).
- **Chord-scale theory.** `chord_scales(chord, key=None)` recommends scales
  to improvise with over a chord (best fit first — Mixolydian over a
  dominant 7th, Dorian over a minor 7th; with a key, the diatonic mode goes
  first, so an `Em7` in C resolves to Phrygian). `chord_scale_notes` spells
  the scale on the chord's root, and `avoid_notes` flags the scale tones a
  half-step above a chord tone (the F over `Cmaj7`).
- **Non-chord-tone analysis.** `analyze_non_chord_tones(melody, chords)`
  labels each melody note against the harmony beneath it — chord tone,
  passing, upper/lower neighbor, suspension, anticipation, appoggiatura, or
  escape tone — judged from how the note is approached and left. Takes a
  single chord for the whole line or one chord per note.
- **Part-writing checker.** `check_voice_leading(voicings)` scans a sequence
  of chord voicings for the classic common-practice errors — parallel
  fifths, parallel octaves, and voice crossing — returning a structured
  issue for each (with SATB voice labels for four-part textures). Clean
  part-writing returns an empty list.
- **Cadence detection.** `detect_cadence(penultimate, final, key, mode)`
  names the harmonic punctuation that ends a phrase — perfect/imperfect
  authentic, half, Phrygian half, deceptive, or plagal — built on the
  existing Roman-numeral analysis and chord voicing (PAC vs IAC depends on
  root position and a tonic soprano). `find_cadences(progression, key)`
  scans a whole progression for cadential motions. Covered in the theory
  guide and the keys-and-harmony skill.
- **Twelve-tone serialism — `ToneRow`.** A new top-level class for the
  twelve-tone technique: build a row from note names or pitch classes and
  get the four operations `P`/`I`/`R`/`RI` (each beginning on the pitch
  class you ask for), any form by label (`row.form("RI7")`), all 48 forms,
  and the printable 12×12 row matrix (`matrix_str()`). Plus
  `is_all_interval` / `interval_succession`. There's a from-scratch guide
  page (`docs/guide/serialism`) that teaches the technique and shows why
  the matrix is self-verifying.
- **Neo-Riemannian transformations.** `Chord` gains the P/L/R operations
  that power Tonnetz harmony and chromatic/film-score writing:
  `parallel()` (P, major↔minor on the same root), `relative()` (R), and
  `leading_tone_exchange()` (L). Chain them with `transform("LP")`, and
  `tonnetz_path(other)` returns the shortest P/L/R route between any two
  triads (e.g. `C → Ab minor` is the hexatonic pole `"PLP"`). Together the
  three reach all 24 major/minor triads.
- **Pitch-class-set toolkit.** `Chord` grows a full post-tonal analysis kit
  on top of the existing `prime_form`/`forte_number`: `interval_vector` (the
  interval-class content `<ic1..ic6>`), `complement` (the rest of the
  aggregate, as a playable chord), and set-class relations between two
  chords — `is_transposition_of` (Tₙ), `is_set_class_equivalent` (TₙI / same
  Forte class, e.g. major ↔ minor triad), `is_z_related` (same interval
  vector, different set class — the all-interval tetrachords 4-z15/4-z29),
  and literal `is_subset_of` / `is_superset_of`.
- **`Score.render()` and `Score.to_wav()`.** Getting audio out of a score
  no longer means importing internals from `pytheory.play` and hand-rolling
  a WAV writer. `score.render()` returns the finished `(N, 2)` float32 mix
  and `score.to_wav("song.wav")` saves a 16-bit stereo file — both headless,
  no speakers or PortAudio required.
- **`Score.ring_out()` — let reverb/delay tails breathe.** Rendering used
  to stop dead on the final beat, clipping the tail of any reverb or delay
  on the last hit (especially noticeable on drum tracks with a long
  reverb). Call `score.ring_out()` once before playing or exporting and it
  appends trailing silence sized automatically to the longest effect tail
  across all parts — pass an explicit `seconds` to override. Opt-in, so
  seamless loops are unaffected. (Resolves #60.) Documented in the effects
  guide and the composing skill.
- **New `"hall"` reverb — and a bug fix.** The `vocal`, `mellotron_flute`,
  and `ring_mod_metallic` instrument presets asked for a `"hall"` reverb
  that never existed, so they silently fell back to the plain algorithmic
  reverb. `"hall"` is now a real convolution space (a warm 2.5-second
  concert hall), so those instruments sound as intended — and it's
  available to everyone as `reverb_type="hall"`.
- **Typos in `reverb_type` now raise** instead of silently falling back to
  the algorithmic reverb — `part()`, `part.set()`, and `set_drum_effects()`
  validate the name and list the valid presets.
- **Stereo reverb is now actually stereo.** The convolution reverb built its
  left and right impulse responses from the same fixed random seed, so both
  channels were identical and the "stereo" reverb had no width. Each channel
  now uses a distinct seed, opening up a real stereo image.
- **Stereo-linked master bus.** The master compressor ran independently on
  the left and right channels, so whenever one side was louder it ducked
  harder and dragged the stereo image off-centre. The bus now detects gain
  reduction from the louder channel and applies one shared gain curve to
  both, keeping the image rock-steady. The old hard brick-wall clip is
  replaced by a soft-knee limiter, so peaks bend into the ceiling with a
  touch of warmth instead of harsh clipping. The bus also strips DC offset
  (the mix sat ~2% off-centre from asymmetric kick/synth waveforms, wasting
  headroom and risking start/stop clicks) with a ~3.5 Hz high-pass that
  leaves the musical bass untouched.
- **Faster rendering.** Convolution impulse responses are memoised per
  `(preset, sample_rate, seed)` — they're deterministic, so they're built at
  most once per process, making re-renders of a reverbed score ~50% faster.
  IR generation itself is also ~15x faster: the per-sample high-frequency
  damping loop is now a vectorised piecewise filter (an inaudible
  approximation), cutting the first render of the benchmark score from
  3.4s to 2.7s.
- **Reproducible renders + a synth cache.** The `noise` and `pluck` synths
  drew from unseeded global randomness, so a score re-rendered slightly
  differently each time. Both are now seeded by pitch (one realisation of
  white noise sounds like any other), making every synth deterministic — so
  the same score renders bit-for-bit identically. That also lets note
  waveforms be memoised across parts and renders: a synth-heavy score
  re-renders ~60% faster.
- **Reliability:** a new `tests/test_dsp_quality.py` makes real assertions
  about the audio itself — oscillator pitch, harmonic content, envelope
  decay, filter response, echo timing, reverb tails, stereo width, panning,
  and the master limiter — so the synth/render core can be optimised without
  silently changing the sound. A companion `tests/test_render_integration.py`
  locks down whole-mix behaviour: pan placement, volume balance, sidechain
  ducking, that effects keep a part's onset time-aligned (the bus is
  zero-latency), and that inert parts are no-ops.
- **Internal:** convolution-reverb presets now have a single source of
  truth (`_IR_DURATIONS`) shared by IR generation, ring-out sizing, the
  reverb-type dispatch, and validation, so preset names and tail lengths
  can't drift.

## 0.53.1

- **More ragas, and reverb on playback.** The raga set grows from 20 to
  36 — adding Ahir Bhairav, Jogiya, Sohni, Puriya, Puriya Dhanashri,
  Shree, Multani, Brindabani Sarang, Megh, Shivaranjani, Tilang,
  Jhinjhoti, Rageshri, Kalavati, Deshkar, and Shankara. `Raga.play()`
  now lays the swaras end to end and mixes a hall reverb over the whole
  phrase (so each note's tail bleeds into the next), with a new
  `Raga.render()` that returns the buffer. Tune it with the `reverb`
  argument or `pytheory raga <name> --play --reverb 0.5`.

## 0.53.0

- **Hindustani ragas — `pytheory.Raga` and `pytheory raga`.** The ten
  thaats described parent scales; this adds twenty of the living ragas
  built on them, each with its ascending line (*aroha*), descending line
  (*avaroha*), catch-phrase (*pakad*), vadi/samvadi, time of day, rasa,
  and jati. `Raga.get("yaman")`, `Raga.by_thaat("kafi")`,
  `Raga.by_time("night")`; `.aroha_tones(sa)` / `.note_names(sa)` voice
  it in any key (Sa is movable). Crucially, ragas render in **just
  intonation** off the bundled 22-shruti ratios — `.just_ratios()`,
  `.shruti_table(sa)` (each swara's ratio and cents off 12-TET), and
  `.play(sa, just=True)` (the default) so a komal Ga or tivra Ma is
  intoned the way it's meant to be heard, not snapped to the tempered
  grid. CLI: `pytheory raga yaman --shruti --play`.
- **SVG fretboard diagrams.** A new `pytheory.diagrams` module renders
  fretboard data as clean, dependency-free SVG you can drop into a
  video, slide, or worksheet — ASCII tabs finally have a graphical
  twin.
  - `Fretboard.tab_image(name)` (and `Fingering.to_svg()`) draw the
    vertical chord box you see in songbooks, with open/muted markers,
    automatic barre detection, and the root highlighted in red.
  - `Fretboard.scale_shapes(scale)` splits a scale into positional
    boxes — the five pentatonic positions, the seven diatonic ones —
    each a small fret window with the roots marked. Boxes follow the
    slant via a notes-per-string cap, so they connect like real CAGED
    shapes. Render one with `shape.to_svg(path=...)`.
  - `Fretboard.arpeggio_diagram(chord)` maps every chord tone across
    the neck, labelled by role (R/3/5/7…), roots highlighted — for
    seeing where the chord lives.
  - SVG is pure text (no dependencies); pass `fmt="png"` to rasterize
    via the optional `cairosvg` package.
- **Metronome and tempo trainer — `pytheory metronome`.** A real-time
  click (accented downbeat, optional subdivisions) that also does two
  practice jobs: `--chords Am F C G` plays a soft chord stab under the
  click, cycling a progression one chord per bar; and `--to`/`--step`/
  `--every` ramp the tempo from a start BPM toward a target, the way
  the phone trainer apps do. Also a library: `pytheory.metronome.Metronome`.
- **Key-level circle of fifths.** `Key.circle_of_fifths()` returns a
  neighborhood map: the dominant and subdominant neighbors with the
  diatonic chords shared with each, the relative and parallel keys, the
  key's signed circle position (sharps positive, flats negative), and
  the twelve-key tour.
- **Chord families by harmonic function.** `Key.chords_by_function()`
  (and `tonic_chords()` / `subdominant_chords()` / `dominant_chords()`)
  group the diatonic triads into tonic (I, iii, vi), subdominant (ii,
  IV), and dominant (V, vii°) families, so you can see which chords are
  interchangeable. Grouping is by scale degree, so it holds for minor
  keys too.
- **Negative harmony.** `Chord.negative_harmony(key)` reflects a chord
  across the tonic↔dominant axis (Ernst Levy / Jacob Collier). `Key.
  negative_harmony()` surfaces the axis, the hinge notes, the negative
  scale and chords, and the *negative dominant* — the minor-subdominant
  reflection of V that bridges the two harmonic families.

## 0.52.0

- **Guitar-aware LilyPond export.** `Score.to_lilypond()` gains
  `chord_names`, `fretboards`, and `tab` flags (plus `chord_part` and
  `fretboard`) that turn a chord part into a lead sheet — a `ChordNames`
  row, a `FretBoards` row, and/or a `TabStaff` driven by a single
  `\chordmode` block. Fret diagrams use PyTheory's *own* voicings (emitted
  via `\storePredefinedDiagram`) so they match what it would play, not
  LilyPond's defaults. Default output is unchanged.

## 0.51.0

- **Custom drum patterns are now first-class.** `Hit` is a public,
  top-level export (`from pytheory import Hit`) — no more reaching for
  the private `pytheory.rhythm._Hit` to build a pattern. The old name
  stays as an alias for back-compat.
- **`score.drums()` accepts a `Pattern` object**, not just a preset
  name string — so a groove you built yourself gets the same
  `repeats`, `fill`, `split`, and `layer` options as the built-ins.
- **`layer=True` on `score.drums()` / `score.add_pattern()`** overlays
  a pattern on top of the existing drums instead of appending it in
  sequence — the supported way to stack grooves and polyrhythms,
  replacing the `_drum_pattern_beats` cursor hack. (#52, #55, #56)

## 0.50.0

- **Real-time chord recognition — `pytheory tune --chords`.** Strum
  and the tuner names the chord: the browser page shows the symbol and
  tones above the strobe, the terminal tuner appends it to the needle
  line, and the SSE/WebSocket stream gains `chord`, `chord_notes`, and
  `chord_confidence` fields. Recognizes major, minor, sus2/sus4, and
  7th chords on all twelve roots, and distinguishes chords from single
  notes.
- **`pytheory.audio.identify_chord()`** — the one-shot "what chord is
  sounding in this buffer?" analyzer behind it. Chromagram with
  harmonic discounting (each pitch class is reduced by the spill it
  receives from 3rd/5th/7th partials of the others — a bright C major
  puts real energy on B via its E's 3rd partial, which is what makes
  naive matchers report Cmaj7), a polyphony gate that rejects single
  notes, and template matching. Calibrated against pytheory's own
  guitar/piano/rhodes renders: 93% on an 81-case battery spanning two
  octaves; silence, noise, and single notes return None.
- `_chromagram` gains `nperseg` and `normalized` options (longer FFT
  windows resolve low voicings; unnormalized frames weight loud
  moments more).

## 0.49.1

- **Fix key detection.** `Key.detect` and `Scale.detect` compared note
  *spellings*, so "A#" never matched a scale spelled with "Bb" — and
  keys whose scales rendered with mixed spellings (A# major contains
  both "A#" and "Bb") got inflated match counts and won far too often.
  Both now compare pitch classes, so enharmonic spelling is irrelevant.
- `Key.detect` breaks ties by whether the candidate's tonic (then its
  fifth) actually occurs in the notes — A-C-E now detects as A minor,
  not C major — and reports conventional key spellings (Bb major, C#
  minor; never theoretical keys like A# major).
- Transcription key detection (`from_wav(split=True)`) now feeds full
  chord tones into `Key.detect` instead of just chord roots — an
  Am-F-G mix detects as C major instead of a spurious sharp key.

## 0.49.0

- **Ableton Link sync — `pytheory live --link`.** The live engine
  joins an Ableton Link session on the local network
  (`engine.enable_link()`): tempo follows the session peer-to-peer,
  the drum pattern locks to the shared beat grid (quantum-aligned, so
  your kick lands on everyone's downbeat), and transport start/stop
  syncs with peers that support it. The TUI header shows the peer
  count. Requires the new `pytheory[link]` extra (LinkPython-extern).
- **Strobe tuner.** `pytheory tune --serve` now serves a strobe
  display — a three-ring segmented disc that drifts clockwise when
  sharp, counter-clockwise when flat, and freezes when you're in tune,
  with the inner rings at half and quarter rate for fine reading.
- **Tuner instrument presets — `pytheory tune --instrument guitar`.**
  Readings lock to the nearest open string (guitar, bass, ukulele,
  violin, viola, cello, mandolin, banjo), so tuning the D string never
  gets misread as "80 cents flat of E". The reading carries a `target`
  field, the browser page highlights the string you're on, and the
  pitch search range widens automatically (bass low E1 = 41 Hz).
  `string_targets()` exposes the (name, frequency) lists, and they
  shift with `--ref`.
- **Tuner WebSocket stream.** The pitch stream is now also served over
  WebSocket at `/ws` (hand-rolled RFC 6455, server-to-client) alongside
  the existing SSE `/stream` — for clients where EventSource is
  awkward.
- **Sus chords and inversions in chord detection.** `detect_chords`
  matches sus2/sus4 templates, and when the bass sits steadily on a
  chord tone that isn't the root, reports the inversion as a slash
  chord ("C/E"). The bass check is a YIN pass on the lowpassed signal
  with a spectral guard against YIN's missing-fundamental phantom (a
  Csus4 with no bass note looks like a phantom F2 — it's rejected
  because no energy actually sits at 87 Hz).
- **Beat-aligned chord windows.** The chord grid aligns itself to the
  music's onsets (circular phase histogram of spectral flux) instead of
  marching from t=0, so a recording that starts mid-bar or with a
  lead-in doesn't smear every chord across two windows. Near-silent
  windows no longer produce junk chords, and the chord chromagram now
  starts at 130 Hz, where FFT bins are finer than a semitone (a loud
  bass note no longer smears into neighboring pitch classes).
- **Slash chords in `Chord.from_symbol`** — `"C/E"` gives the first
  inversion voicing, `"Am7/G"` the third, and a bass note from outside
  the chord (`"C/D"`) is added below the root.

## 0.48.1

- **Docs URL updated to pytheory.org** in package metadata and README
  (the docs site moved from pytheory.kennethreitz.org).

## 0.48.0

- **PyTheory Studio — `pytheory studio`.** A local web app that ties
  the whole listening pipeline together: drag in a recording (.wav,
  .m4a voice memo, .mp3) and the transcription renders as sheet music
  on the page (abcjs); press play to hear it through PyTheory's
  synths; download the MIDI; tuner at the bottom of the page. "Full
  mix" mode runs the four-part bass/melody/chords/drums split.
  Everything runs on localhost — only the notation renderer comes
  from a CDN.
- **7th chords in chord recognition.** `detect_chords` (and therefore
  `from_wav(split=True)`) now matches dominant 7th, major 7th, and
  minor 7th templates alongside triads, with a small prior so plain
  triads aren't promoted by passing melody notes. A rendered
  Dm7-G7-Cmaj7 progression comes back exactly; Am-F-C-G still comes
  back as triads.
- **Fix key detection with 7th-chord symbols** — the chord-root
  extraction mishandled symbols like "Am7".

## 0.47.0

- **Full-arrangement transcription.** `Score.from_wav(split=True)` now
  returns four parts plus the key: `"melody"`, `"bass"`, **`"chords"`**
  (chromagram folded to 12 pitch classes, matched against major/minor
  triad templates per chord window — a rendered Am-F-C-G mix comes back
  exactly), and **`"drums"`** (onset detection on the percussive stem,
  each hit classified as kick/snare/hat by band energy and spectral
  centroid, calibrated against pytheory's own drum synths — including
  kick+hat detected simultaneously). `score.detected_key` carries the
  key via `Key.detect`. Import a song, `play_score(score)`, and you
  have an instant cover version.
- **Real-time tuner — `pytheory tune`.** Microphone → YIN pitch
  tracking → note name and signed cents offset, 20 readings/second.
  Terminal needle by default; `--serve` opens a browser tuner page fed
  by a **Server-Sent Events stream at `/stream`** with CORS open, so
  any JavaScript app can consume PyTheory's pitch detection with three
  lines of `EventSource`. `--ref 442` for orchestras that tune high.
  Python API: `pytheory.tuner.Tuner` and `analyze_frame()`.
- **New public audio analysis functions** — `pytheory.audio.detect_chords`
  and `detect_drums`.
- Docs homepage now shows uv install instructions.

## 0.46.0

- **Full-mix transcription — `Score.from_wav(split=True)`.** Runs
  harmonic-percussive separation first (median-filtered spectrogram
  masks, pure scipy — held notes are horizontal lines on a
  spectrogram, drum hits vertical), then transcribes a `"bass"` part
  and a `"melody"` part from band-split passes. On a four-track test
  mix (drums/bass/Rhodes/lead) the melody came back 15/16 notes
  correct and the bass walked the right roots. Also
  `pytheory transcribe song.wav --split`.
- **Automatic tempo estimation.** `from_wav` now estimates BPM from
  the recording's onset pattern when `bpm=` isn't given
  (autocorrelated spectral flux with a 120-BPM log-gaussian prior);
  a rendered 110 BPM groove estimates exactly 110. Pulse-free rubato
  falls back to 120. `score.bpm` carries the result.
- **Voice memos load directly.** `.m4a`, `.mp3`, and other non-WAV
  formats convert on the fly through `afconvert` (macOS) or `ffmpeg`
  — no manual conversion step.
- **Fix stereo WAV normalization** — stereo int16/int32 files were
  loaded without amplitude scaling (the dtype check ran after the
  channel mixdown converted to float). Transcription was unaffected
  (the pitch tracker is scale-invariant), but `load_wav` output is
  now correctly in [-1, 1].

## 0.45.0

- **Audio import — `Score.from_wav()`.** Record yourself humming a
  melody, whistling a hook, or playing a bass line; load the WAV and
  get an editable Score back — notes, rests, durations, and velocities.
  Pitch tracking is a pure-numpy YIN implementation (no new
  dependencies); transcription is monophonic. Optional `quantize=`
  snaps timing to a grid, `fmin`/`fmax` tighten the search range for
  bass or whistle registers. Also available as `pytheory transcribe
  in.wav out.mid`. Round-trip verified against pytheory's own synth
  output, including repeated-note splitting and the inharmonic piano
  timbre.
- **New piano.** `piano_wave` is now a modal synthesis of stiff steel
  strings: genuinely **inharmonic partials** stretched by string
  stiffness (the 10th partial of middle C rings ~19 cents sharp, just
  like a real piano — verified spectrally), a hammer strike-position
  comb that carves the woody midrange, register-correct stringing (one
  wound bass string up to a beating three-string trichord), and
  frequency-dependent damping so every note darkens as it decays —
  treble notes are short, bass notes bloom. Up to 56 partials in the
  bass (previously 15), so low notes have actual body.
- **Live notes sustain forever.** Sustaining instruments (organ, pads,
  strings, choir — any envelope holding a level ≥ 0.7 whose source is
  still ringing) now loop seamlessly inside their wavetables, so a held
  key rings for as long as you hold it. Percussive instruments (piano,
  plucks, mallets) still decay naturally and end. The loop seam is
  crossfaded, click-free, and works through pitch bends. This removes
  the documented "notes cut off after 3 seconds" limitation.
- **Live effects moved to per-channel buses.** Lowpass, reverb, chorus,
  delay, tremolo, distortion, and saturation now stream per audio block
  with persistent state (filter memory, delay lines, LFO phases) instead
  of being baked into each note's wavetable. MIDI CC sweeps and TUI
  ``fx`` commands apply on the next block (~3ms) with no wavetable
  re-rendering — turning a filter knob mid-phrase no longer stutters.
  The live reverb is now the same Schroeder comb/allpass topology as the
  offline renderer (block-size invariant, verified against the offline
  math), replacing the old multi-tap echo.
- **Live channels honor `detune`, `sub_osc`, and `noise_mix`** — these
  Part parameters were silently ignored by the live engine.
- **`pytheory live`** — the live TUI is now a first-class CLI command
  (``pytheory live [seed] --port --channels --drums --buffer``) instead
  of ``python -m pytheory.live_tui``.
- **Choir vowel transitions.** ``lyric="ah>oo"`` glides the formant
  filters from one vowel to the next across the note — a sung
  diphthong. Chains work too (``"ah>ee>oo"``): each vowel holds, then
  the vocal tract reshapes into the next. Works per-note through
  ``Part.add(..., lyric=...)`` and directly via ``choir_wave()``.

## 0.44.0

- **~11x faster rendering.** The DSP hot paths — Schroeder reverb,
  Karplus-Strong string synthesis, chorus, filter envelopes, the master
  compressor, and several one-pole filters — were per-sample Python
  loops; they now run in C via vectorized `scipy.signal.lfilter`
  recurrences and numpy indexing. A representative 35-second multi-part
  score dropped from 9.1s to 0.8s. Reverb and chorus output is
  bit-identical to 0.43; string synths match to float epsilon. The
  compressor's envelope follower now runs at control rate (32-sample
  blocks with peak detection), which is inaudible but much faster.
  `ensemble=20` parts and the live engine's note-cache misses benefit
  the most.
- **Drum hits by name.** `Part.hit()`, `flam()`, `diddle()`, and
  `cheese()` now accept drum names as plain strings — `kit.hit("kick")`,
  `kit.hit("closed_hat")` — as well as `DrumSound` members. Previously
  strings crashed at render time.
- **`pip install "pytheory[live]"`** now actually works — the `live`
  extra (python-rtmidi) was referenced in error messages but missing
  from packaging.
- **Fix `LiveEngine.export_recording()`** crashing with `AttributeError`
  when called on an engine without the TUI (it referenced a TUI-only
  attribute). Saving a recording from the live TUI works again.
- **Detune oscillators are now cached** per pitch like main oscillators,
  speeding up detuned parts with repeated notes.
- **Documentation overhaul.** New homepage organized around what you
  came for (theory, guitar, composing, live play) with guitar tabs and
  chord identification front and center; new Live Performance guide;
  new API reference pages for the sequencing layer (Score/Part/Pattern)
  and the live engine; custom beat programming and `add_pattern()`
  documented; stale feature counts corrected everywhere (56 waveforms,
  100 drum patterns, 37 fills, 74 percussion sounds, 83 instrument
  presets); Sphinx build is now warning-free.

## 0.43.1

- **Fix `Fretboard.scale_diagram()` enharmonic matching.** Scale notes
  spelled with flats (e.g. the `Eb` blue note in the blues scale) were
  silently omitted from the diagram, because the fretboard spells that
  pitch as `D#`. Notes are now matched enharmonically (by pitch) and
  displayed using the scale's own spelling.

## 0.43.0

- **BREAKING — fingerings now read low-to-high by default.** `Fretboard`
  string lists and `Fingering` positions/string-names now run from the
  **lowest-pitched string first** (e.g. standard guitar reads `E A D G B E`),
  matching how chord diagrams and tablature are conventionally written.
  Previously they ran high-to-low (`E B G D A E`). This affects
  `Fretboard.tones`, iteration over a fretboard, `repr`, `chord()`, `tab()`,
  `chart()`, and `fingering()` output.

  To restore the pre-0.43 high-to-low behavior, pass **`high_to_low=True`**
  to any fretboard constructor — `Fretboard.guitar(high_to_low=True)`,
  `Fretboard(tones=..., high_to_low=True)`, and likewise on every instrument
  preset (`bass`, `ukulele`, `mandolin`, … `keyboard`).

  The flip also applies to **input**: a custom tuning tuple passed to
  `Fretboard.guitar(...)` and manual fret positions passed to
  `fingering(*positions)` are now read in the board's orientation
  (low-to-high by default).

  `to_tab()` and `Part.strum()` are unaffected — they sort by pitch
  internally and produce identical output regardless of orientation.

## 0.42.1

- **Fretboard tuning support** — `to_tab()` now accepts `Fretboard` objects as
  the `tuning` parameter. Works with `Fretboard.guitar()`, `Fretboard.bass()`,
  `Fretboard.ukulele()`, `Fretboard.mandolin()`, `Fretboard.banjo()`, and any
  custom Fretboard with capo.

## 0.42.0

- **LilyPond export** — `Score.to_lilypond()` generates complete LilyPond source
  files with multi-staff scores, key/time signatures, tempo markings, and
  automatic bass clef detection. Output can be compiled to publication-quality
  PDFs with LilyPond.
- **MusicXML export** — `Score.to_musicxml()` generates MusicXML 4.0 documents
  that can be opened in MuseScore, Sibelius, Finale, and any notation software.
  Includes proper ties, chords, clef detection, and tempo/time signature metadata.
- **Guitar/bass tablature** — `Part.to_tab()` and `Score.to_tab()` generate ASCII
  tablature. Supports guitar (6-string), bass (4-string), drop D, and custom
  tunings. Automatically maps notes to the best string/fret positions.

## 0.41.4

- **Fix** — `to_abc()` now ties long notes across barlines instead of emitting
  oversized durations that abcjs can't render (e.g. 16-beat notes become four
  tied whole notes).

## 0.41.3

- **Fix** — `to_abc()` now skips parts with only drum tones or rests (no pitched
  notes), fixing "pitch is undefined" errors in abcjs. Chords are correctly
  recognized as pitched content.

## 0.41.2

- **Auto bass clef** — `to_abc()` detects low-register parts (808, bass, timpani)
  and assigns `clef=bass` automatically based on average note octave.

## 0.41.1

- **Fix** — `to_abc()` no longer crashes on parts containing drum tones.

## 0.41.0

- **ABC notation export** — `Score.to_abc()` converts scores to ABC notation
  strings. Supports multi-voice scores (via `V:` directives), chords, rests,
  accidentals, and all standard durations. Pass `html=True` to get a
  self-contained HTML page that renders sheet music in the browser via abcjs.

## 0.40.9

- **Mellotron synth** — tape-replay keyboard with wow/flutter, tape saturation,
  bandwidth limiting, hiss, and 8-second tape fadeout. Three tape banks via the
  `tape` parameter: `"strings"` (default), `"flute"`, and `"choir"`.
- **Analog oscillator synths** — four new waveform generators for fat, alive,
  analog-style sounds:
  - `Synth.HARD_SYNC` — slave oscillator hard-synced to a master (Prophet-5
    leads). `slave_ratio` parameter controls harmonic content.
  - `Synth.RING_MOD` — two oscillators multiplied for metallic, bell-like
    inharmonic tones. `mod_ratio` parameter.
  - `Synth.WAVEFOLD` — west coast wavefolding (Buchla-style). `folds` parameter
    sweeps from warm to gnarly.
  - `Synth.DRIFT` — analog VCO with pitch drift, jitter, and noise floor.
    `shape` parameter (`"saw"`, `"square"`, `"triangle"`, `"pulse"`) and
    `drift_amount` for instability level.
- **Synth kwargs passthrough** — `play()`, `save()`, and `_render()` now accept
  `**synth_kw` for forwarding parameters to synth wave functions (e.g.
  `play(tone, synth=Synth.MELLOTRON, tape="choir")`).
- **14 new instrument presets** — `mellotron`, `mellotron_strings`,
  `mellotron_flute`, `mellotron_choir`, `sync_lead`, `sync_lead_bright`,
  `ring_mod_bell`, `ring_mod_metallic`, `wavefold_warm`, `wavefold_gnarly`,
  `drift_saw`, `drift_square`, `analog_pad`, `analog_bass`.
- **808 bass envelope fix** — changed from `pluck` (zero sustain, wrong for 808)
  to `piano` (sharp attack with long decay tail).

## 0.40.8

- **Fix hold() inflating duration** — `Note.beats` was returning the full
  duration for held notes (`_hold=True`), causing `Part.total_beats` and
  `Score.duration_ms` to overcount. A part with `hold(Sa, WHOLE * 4)` followed
  by `add(Pa, QUARTER)` would report 17 beats instead of 1. Now held notes
  return 0 beats, matching the renderer which already skipped advancing the
  timeline for held notes.

## 0.40.7

- **Expose missing Synth enum entries** — rhodes, wurlitzer, vibraphone,
  pipe organ, and choir wave functions were already implemented but not
  accessible via the Synth enum. Now available as `Synth.RHODES`,
  `Synth.WURLITZER`, `Synth.VIBRAPHONE`, `Synth.PIPE_ORGAN`, `Synth.CHOIR`.

## 0.40.6

- **Saxophone presets cleaned up** — removed lowpass filters and vel_to_filter
  from all sax instrument presets (saxophone, alto_sax, tenor_sax, bari_sax).
  The saxophone wave function already shapes its own spectrum; the extra
  filters were dulling the tone.

## 0.40.5

- **Saxophone synth overhaul** — reed nonlinearity (asymmetric soft clipping),
  conical bore formant resonances, breath noise with attack envelope, separate
  reed buzz, key click transient, and sub-harmonic warmth. Vibrato dialed back
  to subtle, delayed onset.

## 0.40.4

- **Distortion overhaul** — multi-stage clipping (preamp → power amp →
  asymmetric rectifier) replaces single-stage tanh. Crunch, distorted,
  orange crunch, and metal guitar presets now sound properly driven.

## 0.40.3

- **Crotales synth** — tuned bronze discs with long ring and bright harmonics
- **Tingsha synth** — paired Tibetan cymbals with beating from two detuned discs
- **Rain stick** — cascading pebbles (steep and slow/shallow variants)
- **Ocean drum** — steel beads rolling inside a frame drum, surf wash
- **Cabasa** — metal bead chain on cylinder, bright metallic scrape
- **Wind chimes** — multiple suspended metal tubes ringing at random offsets
- **Finger cymbal** — single zill tap, bright metallic ping
- `crotales`, `tingsha`, `singing_bowl`, `singing_bowl_ring` instrument presets
- Audio demos in docs for all new sounds

## 0.40.2

- **Master compressor dialed back** — threshold raised from 0.5 to 0.7,
  makeup gain capped at 3x. Sparse arrangements no longer get
  over-amplified to clipping.

## 0.40.1

- **Singing bowl synth** — two variants: strike (mallet hit with chirp
  and long decay) and ring (rim-rubbed sustained tone with slow build).
  Inharmonic partials beat against near-degenerate mode pairs for
  authentic Himalayan bowl shimmer.
- `singing_bowl` and `singing_bowl_ring` instrument presets
- Audio demos in docs for both variants

## 0.40.0

- **Rhodes electric piano synth** — tine + tonebar + electromagnetic
  pickup model. `electric_piano` preset now uses dedicated `rhodes_synth`
  instead of FM
- **73 audio demos in docs** — every synth, every drum pattern, every
  code example with `play_score()` now has an embedded audio player
- Idiomatic demos: harp arpeggiates, guitars strum, cello bows, sitar
  drones, strings use ensemble
- Trailing silence trimming on all audio exports
- Raw waveform demos (no envelope) for classic waveforms

## 0.39.3

- **33 audio samples in documentation** — every `play_score()` example
  now has an embedded stereo audio player. Covers quickstart, sequencing,
  drums (all world percussion), playback, and cookbook.
- **`docs/generate_audio.py`** — renders all doc examples to WAV
- Numpy vectorization: cached time arrays, decay envelopes, drum hits;
  vectorized piano harmonic synthesis
- Fixed acid legato example (removed pad envelope, added proper 303 recipe)

## 0.39.2

- **Marching percussion** — snare, rimshot, and stick click sounds with
  high-tension kevlar synthesis and woody-metallic rimshot crack
- **`Part.flam()`**, **`Part.diddle()`**, **`Part.cheese()`** — marching
  rudiment methods for any drum sound
- **`Part ensemble=`** — duplicate voices with per-player timing tendencies
  and micro pitch drift. Works on any Part (drumline, string section, choir).
  `ensemble=20` for a full snare line, `ensemble=4` for a string quartet.
- **Sympathetic resonance** — marching snare buzz builds up with repeated
  hits, decays during rests (like real snare wire response)
- **4 marching patterns** — march, cadence, paradiddle, roll
- **Chakradar tabla pattern** — 16-beat tihai of tihais composition
- Song #32: Snare Cadence (flams, diddles, cheese, triplets, 32nds)

## 0.39.1

- **Chakradar tabla pattern** — 16-beat tihai of tihais composition with
  3 escalating phrases and a crescendo triplet finale

## 0.39.0

- **Dropped `numeral` dependency** — Roman numeral helpers inlined,
  reducing supply chain surface (#47)
- **`Part.ramp()`** — smooth parameter automation with 4 interpolation
  curves (linear, ease_in, ease_out, ease_in_out)
- **Articulations** — staccato, legato, marcato, tenuto, accent, fermata
- **Dynamic curves** — crescendo(), decrescendo(), swell(), dynamics()
- **`Part.hit()`** — individual drum sounds with articulation support
- **Cross-choke drum damping** — djembe, hi-hats, cajón, doumbek
- **5 new djembe patterns** + 3 djembe fills (30 fills total)
- **6 new drum fills** — 3 cajón, 3 metal
- **Duration arithmetic** — multiply, divide, add
- **Improved djembe slap** synthesis
- Song #31: Acid Tabla

## 0.38.2

- **`Part.ramp()`** — smooth parameter automation from current value to
  target over a duration. Works for lowpass, reverb, distortion, chorus,
  delay, volume, and any `.set()` parameter. Four interpolation curves:
  linear, ease_in, ease_out, ease_in_out.

## 0.38.1

- **Dynamic curves** — `Part.crescendo()`, `Part.decrescendo()`,
  `Part.swell()`, and `Part.dynamics()` for velocity ramps and custom
  curves across a sequence of notes

## 0.38.0

- **Articulations** — `staccato`, `legato`, `marcato`, `tenuto`, `accent`,
  `fermata` via `articulation=` on `Part.add()` and `Part.hold()`
- **`Part.hit()`** — place individual drum sounds in a Part's note stream
  with articulation, velocity, and effects support
- **5 new djembe patterns** — dununba, tiriba, yankadi, djansa, mendiani
- **3 new djembe fills** — djembe call, djembe roll, djembe break (30 fills total)
- **Cross-choke drum damping** — striking one sound fades out related sounds
  (djembe, hi-hats, cajón, doumbek)
- **Improved djembe slap** — dry goatskin pop instead of snare-like noise

## 0.37.0

- **5 new djembe patterns** — dununba, tiriba, yankadi, djansa, mendiani
- **3 new djembe fills** — djembe call, djembe roll, djembe break (30 fills total)
- **Cross-choke drum damping** — striking one sound on a hand drum fades
  out the ring of related sounds (djembe slap kills bass resonance, closed
  hat chokes open hat, cajón slap dampens bass, doumbek tek dampens dum)
- **Improved djembe slap** — dry, high-pitched goatskin pop instead of
  snare-like noise rattle

## 0.36.6

- **6 new drum fills** — 3 cajón (flam, rumble, breakdown) and 3 metal
  (triplet, blast, cascade). 27 fills total.
- Updated drums documentation with fill lists and examples

## 0.36.5

- **Duration arithmetic** — `Duration.WHOLE * 2`, `Duration.HALF + Duration.QUARTER`,
  division, and reverse multiply all work now (previously raised TypeError)

## 0.36.3

- **`Part.hold()`** — polyphonic overlap on a single part. Add notes
  without advancing the beat position so they play simultaneously.
  Enables: piano sustain, sitar drone under melody, guitar strum texture.
- **Strum uses hold()** — leading string plays simultaneously with chord,
  no more timing gaps or choppiness
- **Improved songs** 1-16: humanize, velocity dynamics, reverb, saxophone
  for blues
- **Ctrl-C handling** — clean stop on all playback functions
- **REPL updates** — strum, roll, bend, temperament, reference commands
- Song #28 Descent (generative), #29 Pop Rock, #30 Sitar Drone
- 862 tests

## 0.36.1

- **7 new instrument synths:** pedal steel guitar, theremin, kalimba/thumb
  piano, steel drum/pan, accordion (musette reeds), didgeridoo (drone +
  shifting formants), bagpipes (chanter reed)
- **9 new demo moods** in ``pytheory demo``: Theremin Noir, Caribbean,
  Accordion Waltz, Kalimba Dreams, Outback Drone, Highland, Nashville
  Tears, Tabla Fusion
- Improved existing songs with dedicated instrument synths
- 41 synth waveforms, 26+ songs, 21 demo moods

## 0.36.0

- **Banjo synth** — steel strings on drum-head body, nasal twang,
  fast decay with membrane resonance
- **Mandolin synth** — paired steel strings (natural chorus from
  doubled courses), bright body resonance
- **Ukulele synth** — nylon strings, small mid-heavy body, shorter
  sustain than guitar
- **Cajón drums** — bass (woody box thump), slap (snare wire buzz),
  tap (ghost note). 3 patterns: cajon, cajon rumba, cajon folk
- **Vocal/formant synth** — LF glottal model, 5 Peterson & Barney
  formant peaks, jitter/shimmer, consonant onsets, per-note lyrics.
  Presets: vocal, choir
- **Granular synthesis** — grain cloud engine with scatter, pitch
  variation, Hanning windows. Presets: granular_pad, granular_texture
- **Strum sweep** — subtle grace notes before chord hit for natural
  strum feel on all fretboard instruments
- Mandola preset, 34 synth waveforms, 26 songs

## 0.35.0

- **8.5x faster import** — dropped pytuning/sympy, lazy-load scipy.
  `import pytheory` now takes ~50ms instead of ~480ms (#44)
- **Proper shruti JI ratios** — 22 positions with 5-limit just intonation
  (pure 3/2 fifths, 5/4 thirds), not 22-TET approximation
- **Arabic maqam JI ratios** — Zalzalian 11-limit ratios.
  Mi↓ (the Rast third) is exactly 27/22 from Do
- **B#/Cb octave boundary fix** — B#4 = C5, Cb4 = B3 (#45)
- **Int tone names** — `Tone(0, system=TET(22))` works alongside strings.
  Wrapping: `Tone(22)` → tone 0, octave+1. `System.tone()` convenience.
- **Timpani synth** — inharmonic membrane modes, felt mallet, copper kettle
  resonance, cathedral reverb
- **Saxophone synth** — conical bore, reed buzz, brass body warmth.
  4 presets: saxophone, alto_sax, tenor_sax, bari_sax
- **Part.roll()** — rapid repeated notes with velocity ramp for crescendo/
  decrescendo rolls on any instrument
- **Vibrato tuning** — all instruments reduced to 0.001 depth for cleaner
  ensemble sound
- **Granular synthesis** — grain cloud engine with scatter, pitch
  variation, and Hanning-windowed grains. Two presets: granular_pad,
  granular_texture.
- 30 synth waveforms, 838 tests

## 0.34.0

- **16 dedicated instrument synths** — physical modeling and specialized
  synthesis for: piano (hammer + steel strings + soundboard), bass guitar
  (thick KS + pickup), flute (breath + tube resonance), trumpet (lip buzz
  + bell), clarinet (odd harmonics + reed), oboe (double reed + conical
  bore), marimba (inharmonic bar modes), harpsichord (quill pluck),
  cello (deep bowed + body), harp (soft pluck + soundboard bloom),
  upright bass (pizzicato + wooden body), acoustic guitar (KS + body
  resonance), electric guitar (KS + pickup comb filter), sitar (jawari
  + chikari), plus organ and bowed strings
- **Speaker cabinet simulation** — tames distorted guitar fizz
- **Guitar strumming** — `Part.strum("Am")` with fretboard lookup
- **Analog oscillator drift** — subtle per-note pitch wobble on synth presets
- **World percussion:** dhol, dholak, mridangam, djembe, metal kit
  with 22 new drum patterns
- **Piano improvements:** brightness scales with pitch, two-stage decay,
  hammer impact with felt character
- **Vibrato tuning:** reduced across flute, oboe, trumpet, cello for
  smoother ensemble sound
- 27 synth waveforms, 10 envelopes, 40+ instrument presets, 80+ drum patterns

## 0.33.1

- **Electric guitar synth** — Karplus-Strong with magnetic pickup comb filter
  simulation (single-coil honk, proper sustain)
- **Speaker cabinet simulation** — steep rolloff above 4-5kHz with presence
  bump. Makes distorted guitar sound warm instead of fizzy.
- **6 guitar presets:** electric_guitar, clean_guitar, crunch_guitar,
  distorted_guitar, orange_crunch, metal_guitar — all with proper cab sim
- **Sitar synth** — Karplus-Strong with jawari bridge buzz, chikari
  sympathetic strings, variable damping
- **Guitar strumming** — `Part.strum("Am", Duration.HALF)` with
  fretboard fingering lookup, down/up direction, adjustable strum speed
- **World drums:** dhol (bhangra, chaal), dholak (qawwali, folk),
  mridangam (adi talam, korvai), djembe (standard, kuku, soli)
  — all with bandpass-filtered membrane noise for realistic drum head sound
- **Metal drum kit** — clicky kick, bright snare, tight hats
  with 4 patterns (double kick, metal blast, metal groove, metal gallop)
- 15 synth waveforms, 10 envelopes, 40+ instrument presets

## 0.33.0

- **Non-12-TET support** — `TET(n)` factory creates any equal temperament
- **11 microtonal systems:**
  - `"shruti"` (22-TET Indian, 10 thaats with proper shruti intervals)
  - `"maqam"` (24-TET Arabic, quarter-tone Rast/Bayati/Hijaz + 7 more)
  - `"slendro"` (5-TET gamelan), `"pelog"` (9-TET gamelan with 3 pathet)
  - `"thai"` (7-TET, 171 cents/step)
  - `"makam"` (53-TET Turkish Arel-Ezgi-Uzdilek, 9 makams)
  - `"carnatic"` (72-TET, 10 melakartas)
  - `"19-tet"`, `"31-tet"` (historical Western)
  - `"bohlen-pierce"` (13 divisions of the tritave 3:1 — non-octave!)
- **Just intonation** — `temperament="just"` for pure 5-limit ratios
- **Historical pitch** — `Score(reference_pitch=415.0)` for Baroque A=415
- **`Score(system=, temperament=, reference_pitch=)`** flows through to all playback
- Per-system `c_index` and `period` replace hardcoded constants
- Fixed all hardcoded `12`s in tone arithmetic
- Song #22: Greensleeves (Renaissance lute, meantone, A=415)
- 22 new microtonal tests (819 total)

## 0.32.1

- `Tone("X")` now raises `ValueError` immediately instead of silently accepting invalid names (#39)
- Support enharmonic spellings: `Cb`, `Fb`, `E#`, `B#` resolve correctly (#40)
- Support double sharps (`C##`, `Fx`) and double flats (`Dbb`) via semitone arithmetic (#41)
- Accept unicode music symbols: `♯` `♭` `𝄪` `𝄫`

## 0.32.0

- **8 new synth engine features:**
  - Filter envelope: per-note lowpass sweep (`filter_amount`, `filter_attack`, `filter_decay`, `filter_sustain`)
  - Velocity → brightness: harder notes = brighter filter (`vel_to_filter`)
  - Sub-oscillator: octave-below sine for bass weight (`sub_osc`)
  - Tremolo: amplitude LFO modulation (`tremolo_depth`, `tremolo_rate`)
  - Saturation: even-harmonic tape/tube warmth (`saturation`)
  - Noise layer: per-note breath/air texture (`noise_mix`)
  - Phaser: swept allpass filter chain (`phaser`, `phaser_rate`)
  - Configurable FM: `fm_ratio` and `fm_index` params
- **Highpass filter** (12 dB/oct biquad) on any part
- **2 new envelopes:** `bowed` (bow attack with sustain), `mallet` (strike with ringing sustain)
- **Improved `strings_synth`:** additive synthesis with body resonance curve, per-harmonic phase randomization, delayed vibrato onset, bow pressure variation
- **Instrument preset overhaul:** every preset sanity-checked against real instrument behavior
  - Mallet instruments (vibraphone, celesta, music box, glockenspiel, tubular bells) now ring properly
  - Trumpet uses sustaining envelope instead of pluck
  - Woodwinds have breath noise, brass has velocity brightness
  - Bass instruments have sub-oscillators, synth presets have filter envelopes
  - Piano has velocity-to-brightness and subtle hammer noise
- Signal chain: saturation → tremolo → distortion → chorus → phaser → highpass → lowpass → delay → reverb
- Song #21: Cinematic Showcase (Orchestral)

## 0.31.0

- 3 new synth engines: Karplus-Strong pluck, Hammond organ, string ensemble with body formants
- 38 instrument presets: `score.part("lead", instrument="violin")`
- Keys, strings, woodwinds, brass, plucked, synth, and mallet categories
- 13 total synth waveforms

## 0.30.0

- Drums are a real Part — same effects pipeline as any voice
- `score.drums("rock", split=True)` splits kit into kick/snare/hats/toms/cymbals/percussion Parts
- Each split Part gets independent effects (reverb on snare, LP on hats, etc.)
- `set_drum_effects()` applies to all drum Parts (split or not)
- Sidechain triggers on kick only — hats and snare don't duck the pad
- MIDI import via `Score.from_midi(path)`

## 0.29.3

- Drums are now a real Part — same effects pipeline as any other voice, zero code duplication
- `score.parts["drums"]` is a standard Part with reverb, delay, lowpass, etc.
- `set_drum_effects()` is sugar over the Part's attributes

## 0.29.2

- Add `score.set_drum_effects()` — reverb, delay, lowpass, distortion, chorus on the drum bus
- Same effects engine as parts, zero code duplication

## 0.29.1

- Rename song.py → songs.py
- Polish all 20 example songs with stereo, convolution reverb, humanize, detune, sidechain

## 0.29.0

- Add `Score.from_midi(path)` — import any Standard MIDI File into a Score
- Minimal zero-dependency MIDI parser (Type 0 and Type 1)
- Each channel becomes a named Part, channel 10 becomes drum hits
- Tempo, time signature, velocities, and note durations preserved
- Roundtrip: save_midi → from_midi works

## 0.28.3

- Rewrite `pytheory demo` — 8 moods with stereo, effects, humanize, convolution reverb, sidechain
- Added Dub and Temple moods

## 0.28.2

- Lower drum_humanize default to 0.15 — tighter, more professional feel

## 0.28.1

- Humanize drum hits — random timing jitter and velocity variation (default 0.3)
- Control via `Score(drum_humanize=0.5)` — 0.0 = quantized, 0.3 = natural, 0.5+ = loose

## 0.28.0

- Add figured bass notation: `Chord.figured_bass` and `Chord.analyze_figured()` for classical inversion symbols
- Add pitch class set theory: `pitch_classes`, `normal_form`, `prime_form`, `forte_number` on Chord
- Add `Scale.recommend()` — ranked scale suggestions for a set of notes
- Forte number catalog covers all trichords and tetrachords

## 0.27.1

- Tab completion in REPL — context-aware for commands, drum presets, synths, envelopes, chords, notes, systems

## 0.27.0

- Rewrite all 15 drum sounds for higher quality (inharmonic partials, proper transients, multi-mode resonance, saturation)
- 19 example songs including Dance Party at the Reitz House

## 0.26.3

- Stereo drum panning — each sound placed in the stereo field (hat right, crash left, toms spread, kick/snare center)
- Stereo convolution reverb — different IR per L/R channel for all 7 presets
- 2 new songs: Neon Grid (stereo acid), Glass and Silk (sine+triangle waltz)

## 0.26.2

- Stereo convolution reverb — different IR per L/R channel for all 7 presets
- Both algorithmic and convolution reverbs now output true stereo

## 0.26.1

- Stereo reverb — L and R channels get different early reflection patterns for natural width
- Effects chain now skips mono reverb in favor of stereo reverb in the mixer

## 0.26.0

- **Stereo output** — render_score() now returns stereo (N, 2) arrays
- Add `pan` parameter: -1.0 (left) to 1.0 (right), constant-power panning
- Add `spread` parameter: detuned oscillators spread across L/R channels
- Master bus compressor runs per-channel for stereo
- All playback functions handle stereo natively

## 0.25.7

- Add `detune` parameter — ±cents oscillator spread on any synth (3 oscillators per note)
- Swing now applies to drum hits (offbeats shift with the groove)
- Improved snare and hi-hat sounds (metallic harmonics, faster attack)

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
