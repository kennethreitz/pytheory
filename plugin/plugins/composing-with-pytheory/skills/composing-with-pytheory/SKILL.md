---
name: composing-with-pytheory
description: >-
  Compose music with PyTheory — chord progressions, melodies, basslines, drum
  grooves, and full multi-part arrangements written in pure Python and rendered
  to audio or MIDI. Use whenever the user wants to write, sketch, generate, or
  arrange music — "write me a bossa nova in G minor", "make a four-chord pop
  loop", "lay down a funk beat", "turn this progression into a song" — or export
  the result to WAV, MIDI, MusicXML, LilyPond, ABC, or guitar tab.
license: MIT
allowed-tools: Write, Read, Bash(python3:*), Bash(uv run:*)
---

# Composing with PyTheory

PyTheory turns music theory into runnable Python. You build a `Score`, add parts
(chords, melodies, basslines) and drums, then **render it to audio or MIDI** —
every sound is synthesized from math, so there are no samples, plugins, or DAW to
install.

## How to work

1. **Write a short Python script** that builds a `Score` and either plays it or
   saves it. Don't compose by chaining shell one-liners — a script is clearer,
   reproducible, and easy to iterate on.
2. **Run it** with `python3 song.py` (or `uv run python song.py` in a uv project).
3. To let the user *hear* it, call `play_score(score)` (speakers) or render to a
   WAV they can open. To hand off to a DAW, save MIDI.

If PyTheory isn't installed: `pip install pytheory` (add `"pytheory[live]"` only
for live MIDI input).

## Core building blocks

```python
from pytheory import Score, Key, Chord, Duration

score = Score("4/4", bpm=120)          # time signature + tempo

# A part is a voice with its own synth/instrument and effects.
piano = score.part("piano", instrument="piano", reverb=0.3)
lead  = score.part("lead", synth="saw", envelope="pluck", lowpass=4000)
bass  = score.part("bass", synth="triangle", lowpass=900)

# Chords from a Key's progression (Roman numerals) or Chord.from_symbol.
for chord in Key("G", "major").progression("I", "V", "vi", "IV"):
    piano.add(chord, Duration.WHOLE)

# Melodies are note names + durations (a float = beats, or Duration.*).
lead.add("D5", 1).add("B4", 0.5).add("D5", 0.5).add("G5", 2)
lead.rest(2)

for n in ["G2", "D2", "E2", "C2"]:
    bass.add(n, Duration.WHOLE)
```

- `part.add(note_or_chord, duration)` chains and returns the part.
  `part.rest(duration)` inserts silence.
- `Duration.WHOLE / HALF / QUARTER / EIGHTH / SIXTEENTH` plus dotted variants
  (`DOTTED_HALF`, `DOTTED_QUARTER`, …), or pass a float in beats (`1`, `0.5`,
  `0.25`, `0.125`).
- `Key(tonic, mode).progression("I", "V", "vi", "IV")` returns `Chord`s
  (lowercase numeral = minor, e.g. `"i"`, `"VI"`). `Key(...).chords` lists the
  diatonic chords; `Key(...).scale` gives the scale tones. `Chord.from_symbol("F#m7b5")`
  parses any symbol.
- Note names are scientific pitch (`C4` = middle C). `Tone.from_string("A1")`
  builds an explicit pitch; `tone.add(12)`/`tone.add(-12)` shift octaves.

## Expression & dynamics

`add()` takes keyword controls that make lines feel human and musical:

```python
part.add("A4", Duration.HALF, velocity=90, bend=-0.5, articulation="accent")
```

- **`velocity`** (1–127) — loudness per note. Vary it; flat velocities sound
  robotic. Fades are just descending velocities:
  ```python
  for v in [100, 85, 70, 55, 40, 25]:
      part.add("E5", Duration.QUARTER, velocity=v)
  ```
- **`bend`** (semitones, float) — pitch bend over the note's duration. `bend=2`
  bends up a whole step, `bend=-0.5` slides down a quartertone. Great for sitar
  meends, guitar bends, theremin. `bend_type` = `"smooth"` (default), `"linear"`,
  or `"late"`.
- **`articulation`** — `"accent"`, `"staccato"`, `"legato"`, `"marcato"`,
  `"tenuto"`, `"fermata"` (or `""`).
- **`lyric`** — a syllable for vocal synths only (`synth="vocal_synth"` /
  `"choir_synth"`). Passing `lyric` to a non-vocal synth raises an error.
- **`humanize`** (part kwarg, ~0.02–0.2) — subtle timing drift per note.

## Sound design palette

Each part is either an **instrument** preset (realistic) or a raw **synth**
waveform (shapeable), plus an **envelope** and an effects chain.

- **Synths (56)** — `sine`, `saw`, `triangle`, `square`, `pulse`, `fm`, `noise`,
  `supersaw`, `pwm_slow/fast`, `hard_sync`, `ring_mod`, `wavefold`, `drift`, and
  many modeled instruments as `*_synth` (`rhodes_synth`, `sitar_synth`,
  `vocal_synth`, `mellotron_synth`, `singing_bowl_ring_synth`, …).
  `from pytheory.play import Synth; [s.value for s in Synth]` lists them.
- **Instruments (83)** — `piano`, `electric_piano`, `acoustic_guitar`, `cello`,
  `violin`, `harp`, `flute`, `choir`, `vocal`, `sitar`, `koto`, `kalimba`,
  `timpani`, `pipe_organ`, `808_bass`, `acid_bass`, … `from pytheory import
  INSTRUMENTS; sorted(INSTRUMENTS)` lists them.
- **Envelopes (10)** — `none`, `piano`, `organ`, `pluck`, `pad`, `strings`,
  `bowed`, `bell`, `mallet`, `staccato`.

Effects are part kwargs (set once at creation, or change later with `.set()`):

| Group | kwargs |
| --- | --- |
| Level / space | `volume`, `pan` (−1..1), `reverb` (0..1), `reverb_decay`, `reverb_type` |
| Time | `delay`, `delay_time` (beats, e.g. `0.375` dotted-8th, `0.333` triplet), `delay_feedback` |
| Filter | `lowpass`, `lowpass_q`, `highpass`, `highpass_q` (Hz / resonance) |
| Drive | `distortion`, `distortion_drive`, `saturation` |
| Width / pitch | `chorus`, `chorus_rate`, `chorus_depth`, `detune` (**cents**, keep 8–15), `spread` |
| Synth body | `sub_osc` (0..1 sub-oscillator), `tremolo_depth`, `tremolo_rate`, `legato`, `glide` (portamento secs) |
| Mix glue | `sidechain` (0..0.5 duck by the kick), `sidechain_release`, `humanize` |

**`reverb_type`** picks a convolution space: `"algorithmic"` (default),
`"taj_mahal"`, `"cathedral"`, `"plate"`, `"spring"`, `"cave"`,
`"parking_garage"`, `"canyon"`.

```python
pad  = score.part("pad", synth="supersaw", envelope="pad", reverb=0.5,
                  reverb_type="cathedral", sidechain=0.2, sub_osc=0.3)
acid = score.part("acid", synth="saw", envelope="pluck", legato=True, glide=0.05,
                  lowpass=1500, lowpass_q=8, distortion=0.3, distortion_drive=2.0)
```

## Movement: LFOs and mid-track changes

- **`part.lfo(param, rate=, min=, max=, bars=, shape=)`** sweeps a parameter over
  time — the classic filter sweep / auto-wah / tremolo. `rate` is **cycles per
  bar** (`0.5` = one sweep every 2 bars, `1` = once per bar). `shape` =
  `"sine"`, `"triangle"`, `"saw"`, `"square"`.
  ```python
  pad.lfo("lowpass", rate=0.25, min=600, max=5000, bars=8, shape="triangle")
  ```
- **`part.set(**params)`** changes a part's settings partway through, for
  arrangement dynamics (drop the pad back, open the filter for a chorus):
  ```python
  pad.set(volume=0.5, reverb=0.4)
  ```

## Drums

```python
score.drums("hip hop", repeats=4)                       # by preset name
score.drums("rock", repeats=8, fill="rock", fill_every=4)
```

- `score.drums(preset_or_pattern, repeats, fill=, fill_every=, split=, layer=)`.
  Presets include `rock`, `funk`, `jazz`, `hip hop`, `bossa nova`, `salsa`,
  `samba`, `reggae`, `waltz`, `tresillo`, `tabla solo`, … (`Pattern.list_presets()`).
- **Custom beats** — build a `Pattern` from `Hit`s and pass it to `drums()`:
  ```python
  from pytheory import Pattern, Hit, DrumSound
  K, S, CH = DrumSound.KICK, DrumSound.SNARE, DrumSound.CLOSED_HAT
  beat = Pattern("my beat", [
      Hit(K, 0.0), Hit(CH, 0.0), Hit(CH, 0.5),
      Hit(S, 1.0), Hit(CH, 1.0), Hit(CH, 1.5),
      Hit(K, 2.0), Hit(CH, 2.0), Hit(K, 2.5), Hit(CH, 2.5),
      Hit(S, 3.0), Hit(CH, 3.0), Hit(S, 1.75, velocity=35),  # ghost
  ], beats=4.0)
  score.drums(beat, repeats=4)
  ```
  `Hit(sound, position_in_beats, velocity=100)`; 74 `DrumSound` members
  (`print([d.name for d in DrumSound])`) including world kits (`TABLA_*`,
  `CAJON_*`, `DOUMBEK_*`, `DJEMBE_*`).
- **Hand-programmed hits** — `part.hit(DrumSound.KICK, Duration.QUARTER,
  velocity=110, articulation="accent")` places a hit in any part's stream, with
  full per-hit control (good for tabla/cajon fills).
- **Layering / polyrhythm** — repeated `drums()` calls play *in sequence*; pass
  `layer=True` to overlay (clave over a backbeat). For a true polyrhythm, put
  both voices in one `Pattern` at fractional positions.
- **`split=True`** splits a kit into separate `kick`/`snare`/`hats`/`toms`/
  `cymbals`/`percussion` parts so each takes its own effects
  (`score.parts["snare"].set(reverb=0.3)`).
- **`score.set_drum_effects(reverb=, volume=, humanize=, …)`** applies to the
  whole kit at once.

## Arrangement & structure

Real songs are built from repetition and dynamics. Useful idioms:

- **Octave / voicing spread** — layer the same progression across registers:
  ```python
  for c in prog:
      low.add(c.transpose(-12), Duration.WHOLE)
      high.add(c.transpose(12), Duration.WHOLE)
  ```
  `Chord.transpose(semitones)` and `Tone.transpose(semitones)` move pitches.
- **Reusable phrases** — capture a motif as data and replay it with variation:
  ```python
  RIFF = [("A4", 0.5, 90), ("C5", 0.5, 80), ("E5", 1, 100)]
  def play_riff(part, vshift=0):
      for note, dur, vel in RIFF:
          part.add(note, dur, velocity=max(1, min(127, vel + vshift)))
  ```
- **Section boundaries** — rest parts in/out to create intros, breakdowns, drops:
  ```python
  def rest_bars(part, n):
      for _ in range(n):
          part.rest(Duration.WHOLE)
  ```
- **`score.section(name)` / `score.repeat(name, times)`** capture and repeat
  spans for structured arrangements.

## Alternate tunings

PyTheory isn't limited to 12-tone equal temperament:

```python
score = Score("4/4", bpm=75, system="shruti", temperament="just")
```

`system` selects a tuning system (16 available, e.g. `"western"`, `"shruti"`);
`temperament` ∈ `"equal"`, `"just"`, `"meantone"`, etc. Use for raga, microtonal,
and historical-tuning work.

## Hearing it & exporting

```python
from pytheory.play import play_score, render_score, SAMPLE_RATE
import scipy.io.wavfile

play_score(score)                       # play through the speakers

buf = render_score(score)               # float32 (N, 2) buffer, no audio device needed
scipy.io.wavfile.write("song.wav", SAMPLE_RATE, buf)

score.save_midi("song.mid")             # MIDI (drums on channel 10)
open("song.abc", "w").write(score.to_abc(title="Song", key="G"))
open("song.xml", "w").write(score.to_musicxml(title="Song"))
open("song.ly",  "w").write(score.to_lilypond(title="Song", key="G"))
print(score.to_tab("guitar_part"))      # ASCII tab for a part
```

In a headless/CI context (no speakers), prefer `render_score` + WAV over
`play_score`.

## House style (apply unless the user asks otherwise)

- **Detune**: subtle, **8–15 cents**. Never above ~25 — it smears.
- **Humanize**: **0.2** for melodic parts; **0.15** for drums
  (`Score(..., drum_humanize=0.15)`).
- **No swing** unless asked.
- **Sine and triangle are underrated** — reach for them, not just saw/square.
- **Marching music is always 120 BPM.**
- Avoid `strings`-style synths *with detune* for solo classical lines — use a
  cleaner voice.
- If a mix clips, don't crush the synth peaks — add/rebalance parts instead.

## Complete example

```python
from pytheory import Score, Key, Duration
from pytheory.play import play_score

score = Score("4/4", bpm=80, drum_humanize=0.15)
score.drums("hip hop", repeats=4)

piano = score.part("piano", instrument="piano", reverb=0.4, volume=0.4, humanize=0.2)
lead  = score.part("lead", synth="sine", envelope="pluck", detune=10, humanize=0.2,
                   lowpass=2600, delay=0.25, reverb=0.25, volume=0.32)
pad   = score.part("pad", synth="supersaw", envelope="pad", reverb=0.5,
                   reverb_type="cathedral", sidechain=0.2, volume=0.3)
bass  = score.part("bass", synth="triangle", lowpass=800, humanize=0.2, volume=0.5)

prog = Key("A", "minor").progression("i", "VI", "III", "VII")
for c in prog:
    piano.add(c, Duration.WHOLE)
    pad.add(c, Duration.WHOLE, velocity=55)
    bass.add(c.transpose(-24), Duration.WHOLE)

lead.add("E5", 1, velocity=90).add("D5", 1).add("C5", 1).rest(1)
lead.add("A4", 1).add("C5", 0.5).add("D5", 0.5).add("E5", 1).rest(1)
pad.lfo("lowpass", rate=0.25, min=700, max=4000, bars=4, shape="triangle")

play_score(score)   # or render to WAV (see "Hearing it & exporting")
```

## Tips & gotchas

- **`lyric` is vocal-only** — only `vocal_synth` / `choir_synth` accept it.
- **`detune` is in cents**, not semitones — 8–15 is a gentle widening.
- **`lfo` rate is cycles per bar** — for a slow sweep over a whole 8-bar section
  use a small `rate` (e.g. `0.125`) with `bars=8`.
- **Effects are part-level**, not per-note — to vary an effect over time use
  `lfo()` or `set()`, and for per-note expression use `velocity`/`bend`/
  `articulation`.
- `score.drums()` takes a preset **name** or a `Pattern` object.
- Durations are in beats; a whole note fills one 4/4 bar.
- Octave matters — keep bass low (`C2`) and leads up top (`C5`).
- PyTheory can also *identify* chords, build fretboard fingerings, and transcribe
  recordings (`Chord.identify()`, `Fretboard`, `Score.from_wav(...)`). See
  https://pytheory.org.
