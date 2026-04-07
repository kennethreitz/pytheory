# Changelog

All notable changes to PyTheory are documented here.

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
