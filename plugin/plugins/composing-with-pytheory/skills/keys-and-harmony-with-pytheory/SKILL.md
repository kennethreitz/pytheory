---
name: keys-and-harmony-with-pytheory
description: >-
  Analyze and generate keys and chord progressions with PyTheory. Use when the
  user asks what key some notes are in, the diatonic chords of a key, a Roman-
  numeral analysis of a progression, what chord comes next, secondary dominants,
  borrowed chords, chords grouped by function (tonic/subdominant/dominant), the
  key-level circle of fifths, negative harmony, how to modulate between keys
  (pivot chords / modulation path), or to generate a progression. For a single
  chord's voicing/analysis use the chord-lab skill; for full arrangements use the
  composing skill.
license: MIT
allowed-tools: Write, Read, Bash(python3:*), Bash(uv run:*)
---

# Keys & Harmony

Working with keys and *progressions* — the harmonic level above a single chord.

## Keys and their diatonic content

```python
from pytheory import Key

k = Key("C", "major")
k.chords            # ['C major', 'D minor', 'E minor', 'F major', 'G major', 'A minor', 'B diminished']
k.seventh_chords    # ['C major 7th', 'D minor 7th', …, 'G dominant 7th', …]
k.note_names        # ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']
k.signature         # {'sharps': 0, 'flats': 0, 'accidentals': []}
k.relative          # <Key A minor>
```

## Detect the key

```python
Key.detect("C", "E", "G", "B", "D")     # -> <Key C major>
```

## Progressions

```python
k = Key("G", "major")
[c.symbol for c in k.progression("I", "V", "vi", "IV")]   # ['G', 'D', 'Em', 'C']
[c.symbol for c in k.nashville(1, 5, 6, 4)]               # ['G', 'D', 'Em', 'C']
k.random_progression(4)                                    # a diatonic [Chord, …]
```

Roman-numeral **analysis** of an existing progression:

```python
from pytheory import analyze_progression, Chord
chords = [Chord.from_symbol(s) for s in ["C", "G", "Am", "F"]]
analyze_progression(chords, key="C", mode="major")        # ['I', 'V', 'vi', 'IV']
```

**Secondary dominants** — applied dominants that tonicise a non-tonic
degree. `detect_secondary_dominant` *identifies* one chord (the analytical
inverse of `Key.secondary_dominant(degree)`, which *builds* one); pass
`secondary_dominants=True` to `analyze_progression` to label them in
context (instead of the bare degree):

```python
from pytheory import detect_secondary_dominant, analyze_progression, Chord
detect_secondary_dominant(Chord.from_symbol("D7"), "C")   # 'V7/V'  (D7 -> G)
detect_secondary_dominant(Chord.from_symbol("E7"), "C")   # 'V7/vi' (E7 -> Am)
prog = [Chord.from_symbol(s) for s in ("C", "D7", "G7", "C")]
analyze_progression(prog, "C", secondary_dominants=True)  # ['I', 'V7/V', 'V7', 'I']
```

From the terminal, `pytheory analyze C D7 G7 C` prints the whole picture —
detected key, Roman numerals (with secondary dominants), and cadences
(add `--key`/`--mode` to fix the key).

**Cadences** — the harmonic punctuation that ends a phrase. Pass the last
two chords (and the key) to `detect_cadence`, or scan a whole progression
with `find_cadences`:

```python
from pytheory import detect_cadence, find_cadences, Chord
C = Chord.from_name

detect_cadence(C("G"), C("C"), "C")            # 'imperfect authentic' (5th on top)
detect_cadence(C("G"), C("Am"), "C")           # 'deceptive'  (V->vi surprise)
detect_cadence(C("F"), C("C"), "C")            # 'plagal'     (the 'Amen')
detect_cadence(C("Dm"), C("G"), "C")           # 'half'       (ends on V)
detect_cadence(C("E"), C("Am"), "A", "minor")  # 'imperfect authentic'

# Perfect authentic needs the tonic in the soprano (both root position):
pac_I = Chord.from_midi_message(48, 52, 55, 60)   # C3 E3 G3 C4
detect_cadence(C("G"), pac_I, "C")             # 'perfect authentic'

find_cadences([C(n) for n in ("C","F","G","Am")], "C")   # [(2,'half'), (3,'deceptive')]
```

**Non-chord tones** — label the melody notes that *aren't* in the harmony
(passing / neighbor / suspension / anticipation / appoggiatura / escape).
Pass one chord for the whole line, or one chord per note:

```python
from pytheory import analyze_non_chord_tones, Chord, Tone
mel = [Tone.from_string(n) for n in ("C4","D4","E4")]
[r["type"] for r in analyze_non_chord_tones(mel, Chord.from_name("C"))]
# ['chord tone', 'passing', 'chord tone']
```

## Harmonic color & motion

```python
k = Key("C", "major")
k.secondary_dominant(5).symbol     # 'D7'  — the V/V
k.borrowed_chords                  # chords from the parallel minor (modal interchange)
k.suggest_next(Chord.from_symbol("G"))   # ranked next-chord candidates
```

Chords grouped by **harmonic function** (interchangeable within a group), the
key-level **circle of fifths**, and **negative harmony**:

```python
k = Key("C", "major")
k.chords_by_function()   # {'tonic': [C,Em,Am], 'subdominant': [Dm,F], 'dominant': [G,Bdim]}
k.tonic_chords(); k.subdominant_chords(); k.dominant_chords()

cof = k.circle_of_fifths()
cof["position"]                 # 0  (sharps +, flats -)
cof["relative"], cof["parallel"]               # A minor, C minor
cof["dominant"]["key"], cof["dominant"]["shared_chords"]   # G major + the 4 shared chords

neg = k.negative_harmony()       # Levy/Collier reflection across the tonic↔dominant axis
neg["axis"]                      # ('C', 'G')
neg["negative_dominant"]         # Fm — the chord that bridges the two families
neg["scale"], neg["chords"]      # the mirrored scale and diatonic chords
```

## Modulation

```python
src, dst = Key("C", "major"), Key("G", "major")
src.pivot_chords(dst)        # ['A minor', 'C major', 'E minor', 'G major']  — shared chords
src.modulation_path(dst)     # a chord path that carries you from C to G
```

## Hear a progression

```python
from pytheory.play import play_progression
from pytheory import Key
play_progression(Key("G", "major").progression("I", "V", "vi", "IV"), t=700)
```

## Tips

- `progression()` takes Roman numerals (lowercase = minor: `"ii"`, `"vi"`);
  `nashville()` takes degree numbers.
- `analyze_progression(chords, key=, mode=)` returns numerals (or `None` for
  chords outside the key) — handy for "what are these chords doing?".
- To turn a progression into a full track (drums, bass, synths, export), hand off
  to the **composing-with-pytheory** skill.
