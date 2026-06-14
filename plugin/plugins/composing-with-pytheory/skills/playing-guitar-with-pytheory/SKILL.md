---
name: playing-guitar-with-pytheory
description: >-
  Help guitarists and string players with PyTheory — chord fingerings and shapes,
  ASCII tablature, chord identification, scale diagrams, alternate tunings and
  capo, Nashville number charts, and a real-time strobe tuner. Use whenever the
  user asks for a chord shape or fingering ("how do I play F#m7b5"), a tab, what
  chord some frets/notes make, a scale diagram on the fretboard, a drop-D / DADGAD
  / open-G voicing, a capo position, a Nashville chart, or how to tune up — for
  guitar, bass, ukulele, mandolin, banjo, and ~20 other stringed instruments.
license: MIT
allowed-tools: Write, Read, Bash(python3:*), Bash(uv run:*), Bash(pytheory:*)
---

# Playing guitar (and strings) with PyTheory

PyTheory models the fretboard: chord shapes, fingerings, tablature, scale
diagrams, alternate tunings, and chord identification — for guitar and ~20 other
stringed instruments — plus a real-time tuner. The fretboard tools are pure
Python (run a script or one-liner); the tuner is a CLI that listens to your mic.

If PyTheory isn't installed, prefer uv when available: `uv pip install pytheory`
(or `uv add pytheory` in a uv project); otherwise `pip install pytheory`.

## Fingerings, chord shapes & tab

```python
from pytheory import Fretboard, Chord

fb = Fretboard.guitar()

print(fb.tab("Am"))          # ASCII tablature for a chord
# A minor
# E|--x--
# A|--0--
# D|--2--
# G|--2--
# B|--1--
# e|--0--

shape = fb.chord("Am")       # a Fingering object
shape.positions              # (None, 0, 2, 2, 1, 0)  — None = muted string
shape.string_names           # ('E', 'A', 'D', 'G', 'B', 'e')
print(shape.tab())           # same ASCII tab
```

- `Fretboard.guitar()` and friends build a fretboard; `.chord("Cmaj7")` returns
  a **`Fingering`**, `.tab("Cmaj7")` returns the ASCII tab string directly.
- `.fingering(0, 2, 2, 1, 0, 0)` builds a `Fingering` from explicit fret numbers
  (low-to-high), e.g. to check a shape you have in mind.
- A `Fingering` has `.positions`, `.string_names`, `.tones`, `.tab()`,
  `.identify()`, and `.to_chord()`.

> **Charted-chord coverage:** `.chord()`/`.tab()` look the name up in a library of
> ~144 common voicings — every root in major, minor, `5`, `6`, `7`, `m7`,
> `maj7`, `9`, `m9`, `maj9`, and `dim`. Names *outside* that set (e.g. `sus4`,
> `m7b5`, `aug`, `add9`) raise `KeyError`. For those, either build the shape
> yourself with `.fingering(...)`, or work from the chord's notes via
> `Chord.from_symbol("F#m7b5")` (see "Identify a chord"). `CHARTS["western"].keys()`
> lists everything charted.

## Other instruments

All take the same `.chord()` / `.tab()` / `.scale_diagram()` API:

```python
Fretboard.bass()        # E1 A1 D2 G2   (.bass(five_string=True) for a low B)
Fretboard.ukulele()     # G4 C4 E4 A4
Fretboard.mandolin()    # G3 D4 A4 E5
Fretboard.banjo()       # open G 5-string
```

Also available: `mandola`, `octave_mandolin`, `mandocello`, `violin`, `viola`,
`cello`, `double_bass`, `harp`, `pedal_steel`, `oud`, `sitar`, `shamisen`,
`erhu`, `charango`, `pipa`, `balalaika`, `lute`, `twelve_string`.

## Alternate tunings & capo

```python
Fretboard.guitar(tuning="drop d")     # named tunings
Fretboard.guitar(tuning="dadgad")
Fretboard.guitar().capo(2)            # capo at the 2nd fret
```

Named guitar tunings: `standard`, `drop d`, `open g`, `open d`, `open e`,
`open a`, `dadgad`, `half step down`. For anything else, pass a tuple of open-string
notes (low-to-high), e.g. `Fretboard.guitar(tuning=("C2","G2","C3","G3","C4","E4"))`.

## Identify a chord

From notes:

```python
Chord.from_symbol("F#m7b5").identify()      # 'F# half-diminished 7th'
```

From a shape on the neck (great for "what chord is x02210?"):

```python
fb = Fretboard.guitar()
fb.fingering(None, 0, 2, 2, 1, 0).identify()   # 'A minor'
```

## Scale diagrams

```python
from pytheory import TonedScale, Fretboard

scale = TonedScale(tonic="E2", system="western")["minor"]
print(Fretboard.guitar().scale_diagram(scale, frets=5))
#     0   1   2   3   4   5
# E| E | - | F#| G | - | A |
# A| A | - | B | C | - | D |
# ...
```

> Pentatonic and blues scales live in the **`blues`** system, not `western`:
> `TonedScale(tonic="E2", system="blues")["minor pentatonic"]` (also
> `"major pentatonic"`, `"blues"`, `"major blues"`).

## Nashville number charts

```python
from pytheory import Key

prog = Key("G", "major").nashville(1, 4, 5, 1)
[c.symbol for c in prog]      # ['G', 'C', 'D', 'G']
```

## Turn a melody into tab

Write a line as a part, print it as tablature for a guitarist:

```python
from pytheory import Score, Duration

s = Score("4/4", bpm=120)
gtr = s.part("gtr", instrument="acoustic_guitar")
for n in ["E4", "G4", "A4", "B4", "D5", "E5"]:
    gtr.add(n, Duration.QUARTER)

print(s.to_tab("gtr"))
# e|-0--3--5--7-|-10-12|
# B|------------|------|
# ...
```

`Score.to_tab(part_name)` accepts `tuning=` and `frets=` too.

## Tune up — the real-time tuner

A CLI that listens to your microphone (the user runs it themselves — suggest the
`!` prefix so its output lands in the session):

```
$ pytheory tune --instrument guitar      # strobe tuner locked to the 6 strings
$ pytheory tune --instrument guitar --chords   # strum → it names the chord
$ pytheory tune --serve                  # browser strobe page + JS pitch stream
$ pytheory tune --ref 442                # different concert pitch
```

Instrument presets: `guitar`, `bass`, `ukulele`, `violin`, `viola`, `cello`,
`mandolin`, `banjo`. To get the target frequencies programmatically:

```python
from pytheory.tuner import string_targets
string_targets("guitar")    # [('E2', 82.4), ('A2', 110.0), ('D3', 146.8), ...]
string_targets("guitar", reference_pitch=442)   # shifted concert pitch
```

## Tips & gotchas

- `.chord()` returns a `Fingering`; `.tab()` returns the printable string. Use
  `.tab()` when you just want to show the user a chart.
- Muted strings are `None` in `.positions` and `x` in the tab.
- Tunings are low-to-high tuples of open-string notes; capo with `.capo(n)`.
- Pentatonic/blues scales are in the `blues` system, not `western`.
- The tuner needs a microphone, so it's a CLI the *user* runs (`pytheory tune`),
  not something to call from a rendering script.
- Composing a full arrangement (chords, drums, synths, MIDI/WAV export) is the
  job of the **composing-with-pytheory** skill — this one is about the fretboard
  and tuning.
