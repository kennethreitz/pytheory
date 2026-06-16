---
name: chord-lab-with-pytheory
description: >-
  Build, voice, and analyze individual chords with PyTheory. Use when the user
  asks about a single chord — its notes/intervals, inversions or drop-2/drop-3/
  open voicings, the tritone substitution, what extensions it can take, how
  tense or dissonant it is, its Forte number / pitch-class set, figured bass, or
  the voice-leading between two chords. For progressions and keys use the
  keys-and-harmony skill; for fingerings/tab use the guitar skill.
license: MIT
allowed-tools: Write, Read, Bash(python3:*), Bash(uv run:*)
---

# Chord Lab

Everything about a *single* chord — construction, voicing, and analysis.

## Build a chord

```python
from pytheory import Chord

Chord.from_symbol("F#m7b5")     # widest parser: sus, add9, alterations, slash
Chord.from_name("Am")           # plain names (major/minor/7/maj7/dim/…)
Chord.from_intervals("C", 0, 4, 7)   # root + semitone intervals
Chord.from_tones("C", "E", "G")      # explicit notes
```

A `Chord` has `.symbol`, `.tones` (list of `Tone`), `.root`, and
`.transpose(semitones)`.

## Voicings

`inversion`, `drop2`, `drop3`, and `open_voicing` return a new `Chord`. The
**chord symbol stays the same** — the change is in the *tones* (order/octave), so
inspect `.tones`:

```python
c = Chord.from_symbol("Cmaj7")
[str(t) for t in c.tones]                  # ['C4', 'E4', 'G4', 'B4']
[str(t) for t in c.inversion(1).tones]     # ['E4', 'G4', 'B4', 'C5']
[str(t) for t in c.drop2().tones]          # ['G3', 'C4', 'E4', 'B4']
[str(t) for t in c.open_voicing().tones]   # ['C4', 'E5', 'G4', 'B5']
```

`drop3()` exists too. Use these to spread a close voicing for piano/strings/guitar.

## Analysis

```python
c = Chord.from_symbol("Cmaj7")

c.intervals            # [4, 3, 4]   semitone steps between stacked tones
c.pitch_classes        # {0, 4, 7, 11}
c.forte_number         # '4-20'      set-theory label
c.figured_bass         # '7'
c.extensions()         # [<Tone D5>, <Tone A5>]   available 9/11/13 tones
c.tension              # {'score': 0.15, 'tritones': 0, 'minor_seconds': 1,
                       #  'has_dominant_function': False}
c.dissonance           # 5.33  (a roughness number; higher = more dissonant)
c.beat_frequencies     # [(Tone, Tone, hz), …]  beating between pairs in ET
```

## Reharmonization & voice leading

```python
Chord.from_symbol("G7").tritone_sub()        # -> Db7 (the classic sub)

# Negative harmony — mirror across a key's tonic↔dominant axis (Levy/Collier):
Chord.from_symbol("C").negative_harmony("C").identify()    # 'C minor'
Chord.from_symbol("G7").negative_harmony("C")              # the negative dominant
# (Key("C","major").negative_harmony() gives the axis, hinge notes, and bridge
#  chord — that's the keys-and-harmony skill.)

# Smoothest motion from one chord to the next, voice by voice:
for frm, to, semis in Chord.from_symbol("Cmaj7").voice_leading(Chord.from_symbol("Fmaj7")):
    print(frm, "->", to, f"({semis:+d} semitones)")
```

## Hear a chord

```python
from pytheory.play import play, save
from pytheory import Chord, Synth

play(Chord.from_symbol("Cmaj7"), t=2000)             # through the speakers
save(Chord.from_symbol("Cmaj7"), "chord.wav", t=2000, synth=Synth.TRIANGLE)
```

## Tips

- Voicing methods change `.tones`, not `.symbol` — compare the tone lists.
- `tension` returns a dict; `tension["score"]` is the scalar.
- To *identify* a chord from notes or fret positions, that's the guitar skill
  (`Fingering.identify()`) or `Chord(...).identify()`.
