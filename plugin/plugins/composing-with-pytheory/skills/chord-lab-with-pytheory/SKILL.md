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

### Pitch-class-set toolkit

```python
c = Chord.from_symbol("Cmaj7")

c.normal_form          # (11, 0, 4, 7)   most compact ordering
c.prime_form           # (0, 1, 5, 8)    canonical set-class form
c.interval_vector      # (1, 0, 1, 2, 2, 0)  interval-class content <ic1..ic6>
c.complement           # Chord of the other 8 pitch classes

# Set-class relationships between two chords:
Chord.from_symbol("C").is_transposition_of(Chord.from_symbol("G"))   # True (Tn)
Chord.from_symbol("C").is_set_class_equivalent(Chord.from_symbol("Cm"))  # True (TnI: maj/min)
Chord.from_symbol("C").is_subset_of(Chord.from_symbol("Cmaj7"))      # True
# Z-relation — same interval vector, different set class (e.g. 4-z15 / 4-z29):
a, b = Chord.from_midi_message(0,1,4,6), Chord.from_midi_message(0,1,3,7)
a.is_z_related(b)      # True
```

## Reharmonization & voice leading

```python
Chord.from_symbol("G7").tritone_sub()        # -> Db7 (the classic sub)

# Negative harmony — mirror across a key's tonic↔dominant axis (Levy/Collier):
Chord.from_symbol("C").negative_harmony("C").identify()    # 'C minor'
Chord.from_symbol("G7").negative_harmony("C")              # the negative dominant
# (Key("C","major").negative_harmony() gives the axis, hinge notes, and bridge
#  chord — that's the keys-and-harmony skill.)

# Reharmonization ideas for a chord in a key (tritone sub, diatonic subs,
# secondary dominant, negative harmony) — one dict per suggestion:
from pytheory import reharmonize
for s in reharmonize(Chord.from_symbol("G7"), "C"):
    print(s["technique"], "->", s["chord"].identify())
# Or from the shell: pytheory reharmonize G7 --key C   (--json / --play too)

# Reharmonize a whole progression (techniques: secondary_dominants/tritone/diatonic):
from pytheory import reharmonize_progression
prog = [Chord.from_symbol(s) for s in ("C","Am","Dm","G7","C")]
[c.symbol for c in reharmonize_progression(prog, "C", technique="secondary_dominants")]
# ['C','E7','Am','A7','Dm','D7','G7','C']  — the cycle-of-dominants reharm

# Smoothest motion from one chord to the next, voice by voice:
for frm, to, semis in Chord.from_symbol("Cmaj7").voice_leading(Chord.from_symbol("Fmaj7")):
    print(frm, "->", to, f"({semis:+d} semitones)")
```

### Neo-Riemannian (P/L/R) — chromatic triad moves

The P/L/R transformations move a single voice to flip a major/minor triad
into another — the engine behind Tonnetz harmony and a lot of film-score
chromaticism. Each is its own inverse; together they reach all 24 triads.

```python
C = Chord.from_symbol("C")
C.parallel().identify()              # 'C minor'  (P: same root, flip quality)
C.relative().identify()              # 'A minor'  (R: relative)
C.leading_tone_exchange().identify() # 'E minor'  (L: Leittonwechsel)

C.transform("LP").identify()         # 'E major'  (apply a sequence)
C.tonnetz_path(Chord.from_symbol("Am"))   # 'R'    — shortest P/L/R route between triads
C.tonnetz_path(Chord.from_symbol("Abm"))  # 'PLP'  — the hexatonic pole of C major
```

### Part-writing checker (parallels / crossing)

`check_voice_leading` flags the common-practice no-no's across a sequence of
voicings. Each voicing's tones are read low-to-high as the voices (so a
4-note chord gets bass/tenor/alto/soprano labels):

```python
from pytheory import Chord, check_voice_leading

a = Chord.from_midi_message(48, 55)        # C3 + G3 (a fifth)
b = Chord.from_midi_message(50, 57)        # D3 + A3 (a fifth) — both rise
check_voice_leading([a, b])
# [{'type': 'parallel fifths', 'chords': (0, 1), 'voices': (0, 1),
#   'description': 'parallel fifths between voice 1 and voice 2 (chords 0→1)'}]
```

It catches **parallel fifths**, **parallel octaves**, and **voice
crossing**; clean part-writing returns `[]`.

### Chord-scale theory (what to solo with)

```python
from pytheory import Chord, chord_scales, chord_scale_notes, avoid_notes

chord_scales(Chord.from_symbol("G7"))                 # ['mixolydian']
chord_scales(Chord.from_symbol("Cm7"))                # ['dorian','aeolian','phrygian']
chord_scales(Chord.from_symbol("Em7"), key="C")       # ['phrygian', …]  diatonic mode first
[t.name for t in chord_scale_notes(Chord.from_symbol("Cmaj7"))]  # C D E F G A B
[t.name for t in avoid_notes(Chord.from_symbol("Cmaj7"))]        # ['F']  (½-step above the 3rd)
```

`chord_scales` ranks scales by fit (quality alone, or the diatonic mode
first when you pass a `key`); `avoid_notes` flags scale tones a half-step
above a chord tone.

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
