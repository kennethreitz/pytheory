---
name: scales-modes-and-tunings-with-pytheory
description: >-
  Explore scales, modes, tones, and tuning systems with PyTheory. Use when the
  user asks about a scale or mode (notes of D dorian, harmonize a scale), which
  scale to solo with over some notes, intervals between notes, the overtone
  series, the circle of fifths, microtonal / non-Western systems (raga, maqam,
  gamelan, 19-TET, just/meantone temperament), or note↔frequency↔MIDI
  conversions. For chords/keys use the chord-lab or keys-and-harmony skills.
license: MIT
allowed-tools: Write, Read, Bash(python3:*), Bash(uv run:*)
---

# Scales, Modes & Tunings

Scales and modes, the notes/intervals beneath them, and PyTheory's 16 tuning
systems.

## Scales & modes

```python
from pytheory import TonedScale

ts = TonedScale(tonic="C4", system="western")
ts.scales                       # ('chromatic','major','minor','dorian','lydian', …)

s = ts["dorian"]
s.note_names                    # ['C', 'D', 'Eb', 'F', 'G', 'A', 'Bb', 'C']
[str(t) for t in s.tones]       # ['C4', 'D4', 'Eb4', 'F4', …]
s.harmonize()                   # diatonic chords built on each degree
```

> **Pentatonic & blues** scales live in the `blues` system, not `western`:
> `TonedScale(tonic="E2", system="blues")["minor pentatonic"]` (also
> `"major pentatonic"`, `"blues"`, `"major blues"`).

## Which scale fits these notes?

`Scale.recommend` ranks scales by how well they contain a set of notes — great
for "what can I solo with here?". Note the import: `pytheory.Scale` is an alias
for `TonedScale`, so import the real class from `pytheory.scales`:

```python
from pytheory.scales import Scale
Scale.recommend("C", "Eb", "G", "Bb", "D", top=3)
# [('C', 'aeolian', 1.0), ('G', 'aeolian', 1.0), ('C', 'dorian', 1.0)]
# -> (tonic, scale_name, fitness 0..1)
```

Detect the scale of a note set:

```python
TonedScale(tonic="C4", system="western")["major"].detect("C","D","E","F","G","A","B")
# ('C', 'major', 7)   -> (tonic, scale, matched-note count)
```

## Tones, intervals, overtones

```python
from pytheory import Tone

Tone.from_string("A4").frequency          # 440.0
Tone.from_midi(69)                        # <Tone A4>
Tone.from_frequency(440.0)                # <Tone A4>
Tone.from_string("C4").interval_to(Tone.from_string("G4"))   # 'perfect 5th'
Tone.from_string("A2").overtones(4)       # [110.0, 220.0, 330.0, 440.0]
[str(t) for t in Tone.from_string("C4").circle_of_fifths()]  # ['C4','G4','D5','A5', …]
```

## Tuning systems & temperaments

```python
from pytheory import SYSTEMS
list(SYSTEMS)        # 16: 'western','indian','arabic','japanese','blues',
                     # 'gamelan','19-tet','31-tet','shruti', …
```

Build scales in any system, e.g. an Indian raga or Arabic maqam:

```python
TonedScale(tonic="C4", system="indian").scales      # available ragas
TonedScale(tonic="C4", system="arabic")["..."]      # maqamat
```

Temperament affects the actual pitch (Hz) of a tone:

```python
Tone.from_string("E4").pitch(temperament="just")    # 330.0 (vs ~329.6 equal)
# Whole-score tuning: Score("4/4", bpm=90, system="shruti", temperament="just")
```

## Tips

- `Scale.recommend` and `Scale.detect`-style helpers take **note name strings**.
- `pytheory.Scale` is aliased to `TonedScale`; the static `recommend` lives on
  `pytheory.scales.Scale`.
- Temperaments include `equal` (default), `just`, `meantone`, `pythagorean`.
- To actually *play* in an alternate system, pass `system=`/`temperament=` to
  `Score(...)` (see the composing skill).
