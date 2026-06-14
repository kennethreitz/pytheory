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
   saves it. Don't try to compose by chaining shell one-liners — a script is
   clearer and reproducible.
2. **Run it** with `python3 your_script.py` (or `uv run python your_script.py`
   inside a project that uses uv).
3. To let the user *hear* it, either call `play_score(score)` (plays through the
   speakers) or render to a WAV they can open. To hand off to a DAW, save MIDI.

If PyTheory isn't installed: `pip install pytheory` (add `pip install
"pytheory[live]"` only if they need live MIDI input).

## Core building blocks

```python
from pytheory import Score, Key, Chord, Duration

score = Score("4/4", bpm=120)          # time signature + tempo

# A part is a voice with its own synth/instrument and effects.
piano = score.part("piano", instrument="piano", reverb=0.3)
lead  = score.part("lead", synth="saw", envelope="pluck", lowpass=4000)
bass  = score.part("bass", synth="triangle", lowpass=900)

# Chords come from a Key's progression (Roman numerals) or Chord.from_symbol.
for chord in Key("G", "major").progression("I", "V", "vi", "IV"):
    piano.add(chord, Duration.WHOLE)

# Melodies are note names + durations (a float = beats, or Duration.*).
lead.add("D5", 1).add("B4", 0.5).add("D5", 0.5).add("G5", 2)
lead.rest(2)

# Basslines the same way.
for n in ["G2", "D2", "E2", "C2"]:
    bass.add(n, Duration.WHOLE)
```

- `part(name, ...)` — `instrument="piano"` picks a preset; `synth="saw"` picks a
  raw waveform. Effects are kwargs: `reverb`, `delay`, `chorus`, `distortion`,
  `lowpass`, `highpass`, `detune`, `pan`, `humanize`, `volume`.
- `part.add(note_or_chord, duration)` returns the part, so calls chain.
  `part.rest(duration)` inserts silence.
- `Duration.WHOLE / HALF / QUARTER / EIGHTH / SIXTEENTH`, or pass a float in
  beats (`1`, `0.5`, `0.25`).
- `Key(tonic, mode).progression("I", "V", "vi", "IV")` returns `Chord`s;
  `Key(...).chords` lists the diatonic chords. `Chord.from_symbol("F#m7b5")`
  parses any symbol.

## Drums

```python
score.drums("rock", repeats=8, fill="rock", fill_every=4)
```

- `score.drums(preset, repeats, fill=..., fill_every=..., split=..., layer=...)`.
  Presets include `rock`, `funk`, `jazz`, `bossa nova`, `salsa`, `samba`,
  `reggae`, `waltz`, and more (`Pattern.list_presets()` for the full list).
- **Custom beats** — build a `Pattern` from `Hit`s and pass it straight to
  `drums()`:

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

  `Hit(sound, position_in_beats, velocity=100)` — `0.0` is beat 1, `0.5` the
  following eighth, `0.25` a sixteenth. There are 74 `DrumSound` members
  (`print([d.name for d in DrumSound])`).
- **Layering / polyrhythm** — repeated `drums()` calls play *in sequence* by
  default. Pass `layer=True` to overlay a groove on top of the existing drums
  (e.g. a clave over a backbeat). For a true polyrhythm, put both voices in one
  `Pattern` at their fractional positions.

## Hearing it & exporting

```python
from pytheory.play import play_score, render_score, SAMPLE_RATE
import scipy.io.wavfile

play_score(score)                       # play through the speakers

buf = render_score(score)               # float32 (N, 2) numpy buffer, no audio device needed
scipy.io.wavfile.write("song.wav", SAMPLE_RATE, buf)   # save WAV

score.save_midi("song.mid")             # MIDI (drums on channel 10)
open("song.abc", "w").write(score.to_abc(title="Song", key="G"))
open("song.xml", "w").write(score.to_musicxml(title="Song"))
open("song.ly",  "w").write(score.to_lilypond(title="Song", key="G"))
print(score.to_tab("guitar_part"))      # ASCII guitar tab for a part
```

In a headless or CI context (no speakers), prefer `render_score` + WAV over
`play_score`.

## House style (apply these unless the user asks otherwise)

- **Detune**: keep it subtle, **8–15**. Never go above ~25 — it smears.
- **Humanize**: **0.2** is the sweet spot for melodic parts; **0.15** for drums
  (`Score(..., drum_humanize=0.15)`).
- **No swing** unless the user specifically asks for it.
- **Sine and triangle are underrated** — reach for them, not just saw/square.
- **Marching music is always 120 BPM.**
- Avoid `strings`-style synths *with detune* for solo classical lines — it sounds
  bad; use a cleaner voice there.
- If a mix clips, don't crush the synth peaks — add more parts / rebalance
  instead.

## Complete example — a pop loop you can hear

```python
from pytheory import Score, Key, Duration
from pytheory.play import play_score

score = Score("4/4", bpm=110, drum_humanize=0.15)
score.drums("rock", repeats=8, fill="rock", fill_every=4)

pads = score.part("pads", synth="triangle", envelope="pad", reverb=0.4, volume=0.35)
lead = score.part("lead", synth="sine", envelope="pluck", detune=10, humanize=0.2,
                  delay=0.2, reverb=0.2)
bass = score.part("bass", synth="triangle", lowpass=900)

prog = Key("C", "major").progression("I", "V", "vi", "IV") * 2
for chord in prog:
    pads.add(chord, Duration.WHOLE)

lead.add("E5", 1).add("D5", 0.5).add("E5", 0.5).add("G5", 2)
lead.add("C5", 1).add("D5", 1).add("E5", 1).rest(1)

for root in ["C2", "G2", "A2", "F2"] * 2:
    bass.add(root, Duration.WHOLE)

play_score(score)   # or: render to WAV (see "Hearing it & exporting")
```

## Tips & gotchas

- `score.drums()` takes a preset **name** or a `Pattern` object — both get the
  same `repeats`/`fill`/`split`/`layer` options.
- `split=True` on `drums()` splits a kit into separate `kick`/`snare`/`hats`/…
  parts so each can take its own effects (`score.parts["snare"].reverb = 0.3`).
- Durations are in beats; a "whole note" fills one 4/4 bar.
- Note names are scientific pitch (`C4` = middle C). Octave numbers matter for
  range — keep bass low (`C2`) and leads up top (`C5`).
- Want PyTheory to also *identify* a chord from notes, build fretboard
  fingerings, or transcribe a recording? Those live in the same library
  (`Chord.identify()`, `Fretboard`, `Score.from_wav(...)`) — see
  https://pytheory.org.
