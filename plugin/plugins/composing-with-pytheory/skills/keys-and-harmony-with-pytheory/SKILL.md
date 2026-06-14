---
name: keys-and-harmony-with-pytheory
description: >-
  Analyze and generate keys and chord progressions with PyTheory. Use when the
  user asks what key some notes are in, the diatonic chords of a key, a Roman-
  numeral analysis of a progression, what chord comes next, secondary dominants,
  borrowed chords, how to modulate between keys (pivot chords / modulation path),
  or to generate a progression. For a single chord's voicing/analysis use the
  chord-lab skill; for full arrangements use the composing skill.
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

## Harmonic color & motion

```python
k = Key("C", "major")
k.secondary_dominant(5).symbol     # 'D7'  — the V/V
k.borrowed_chords                  # chords from the parallel minor (modal interchange)
k.suggest_next(Chord.from_symbol("G"))   # ranked next-chord candidates
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
