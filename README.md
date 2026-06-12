# PyTheory: Music Theory for Humans

Explore music theory, compose multi-part arrangements, and export to MIDI — all in Python.

```
$ pip install pytheory
```

## Sketch Ideas Fast

```python
from pytheory import Score, Pattern, Key, Duration, Chord
from pytheory.play import play_score

score = Score("4/4", bpm=140)
score.drums("bossa nova", repeats=4)

chords = score.part("chords", synth="fm", envelope="pad", reverb=0.4)
lead = score.part("lead", synth="saw", envelope="pluck", delay=0.3, lowpass=3000)
bass = score.part("bass", synth="sine", lowpass=500)

for sym in ["Am", "Dm", "E7", "Am"]:
    chords.add(Chord.from_symbol(sym), Duration.WHOLE)
    chords.add(Chord.from_symbol(sym), Duration.WHOLE)

lead.arpeggio("Am", bars=2, pattern="updown", octaves=2)
lead.arpeggio("Dm", bars=2, pattern="updown", octaves=2)
lead.set(lowpass=5000, reverb=0.4)
lead.arpeggio("E7", bars=2, pattern="up", octaves=2)
lead.arpeggio("Am", bars=2, pattern="updown", octaves=2)

for n in ["A2", "E2", "A2", "C3"] * 4:
    bass.add(n, Duration.QUARTER)

play_score(score)              # hear it now
score.save_midi("sketch.mid")  # open in your DAW
```

## Hear It Instantly

```
$ pytheory demo
```

## Music Theory

```pycon
>>> from pytheory import Key, Chord, Tone

>>> Key("C", "major").chords
['C major', 'D minor', 'E minor', 'F major', 'G major', 'A minor', 'B diminished']

>>> [c.symbol for c in Key("G", "major").progression("I", "V", "vi", "IV")]
['G', 'D', 'Em', 'C']

>>> Chord.from_symbol("F#m7b5").identify()
'F# half-diminished 7th'

>>> Tone.from_string("C4").interval_to(Tone.from_string("G4"))
'perfect 5th'

>>> Key("C", "major").pivot_chords(Key("G", "major"))
['A minor', 'B minor', 'C major', 'D major', 'E minor', 'G major']

>>> Chord.from_tones("C", "E", "G").forte_number
'3-11'

>>> from pytheory.scales import Scale
>>> Scale.recommend("C", "Eb", "F", "Gb", "G", "Bb", top=3)
[('C', 'blues', 1.0), ...]
```

## Guitar

Chord fingerings, tabs, and scale diagrams for guitar and 24 other
stringed instruments:

```pycon
>>> from pytheory import Fretboard

>>> print(Fretboard.guitar().tab("Am"))
A minor
E|--x--
A|--0--
D|--2--
G|--2--
B|--1--
e|--0--

>>> Fretboard.guitar().chord("G")
Fingering(E=3, A=2, D=0, G=0, B=0, e=3)
```

Melodies and basslines render to ASCII tablature with `part.to_tab()`,
and chord charts work in Nashville numbers too.

## Composition

```python
score = Score("4/4", bpm=124)
score.drums("house", repeats=16, fill="house", fill_every=8)

pad = score.part("pad", synth="supersaw", envelope="pad",
                 reverb=0.5, chorus=0.3, sidechain=0.85)
lead = score.part("lead", synth="saw", envelope="pluck",
                  legato=True, glide=0.03, humanize=0.3)
bass = score.part("bass", synth="sine", lowpass=300, sidechain=0.7)

# Song structure
score.section("verse")
# ... add notes ...
score.section("chorus")
lead.set(lowpass=5000, reverb=0.3)
# ... add notes ...
score.end_section()

score.repeat("verse")
score.repeat("chorus", times=2)
```

## 56 Synth Waveforms

The 10 classics — sine, saw, triangle, square, pulse, FM, noise, supersaw, PWM slow, PWM fast — plus 46 modeled instruments (Rhodes, Wurlitzer, pipe organ, vibraphone, choir, sitar, theremin, and more), with detune, stereo pan, and spread.

## 100 Drum Patterns

rock, jazz, bebop, bossa nova, salsa, samba, afrobeat, funk, reggae, house, trap, metal, drum and bass — and 87 more. Plus 37 fill presets and 74 synthesized percussion sounds. Stereo panned like a real kit.

## 6 Effects with Automation

```python
lead = score.part("lead", synth="saw",
                  distortion=0.7, lowpass=1000, lowpass_q=5.0,
                  delay=0.3, reverb=0.4, reverb_type="plate",
                  chorus=0.3)

# Automate mid-song
lead.set(lowpass=4000, distortion=0.9)

# LFO modulation
lead.lfo("lowpass", rate=0.5, min=400, max=3000, bars=8)
```

Signal chain: distortion → chorus → lowpass → delay → reverb. Sidechain compression. Master bus compressor/limiter. Stereo output.

## Convolution Reverb

7 synthetic impulse responses: Taj Mahal (12s), cathedral, plate, spring, cave, parking garage, canyon.

```python
pad = score.part("pad", synth="supersaw",
                 reverb=0.85, reverb_type="taj_mahal")
```

## 6 Musical Systems

Western, Indian (Hindustani), Arabic (Maqam), Japanese, Blues/Pentatonic, Javanese Gamelan — 40+ scales.

## 83 Instrument Presets

Guitar (8 tunings), bass, ukulele, mandolin family, violin family, banjo, harp, oud, sitar, erhu, and more — with chord fingering generation for 25 stringed instruments.

## Command Line

```
$ pytheory repl                            # interactive scratchpad
$ pytheory demo                            # hear a generated track
$ pytheory key G major                     # explore a key
$ pytheory identify Cmaj7                  # analyze a chord symbol
$ pytheory progression C major I V vi IV   # build a progression
$ pytheory midi C major I V vi IV -o out.mid
$ pytheory play Am7 --synth saw --envelope pluck
$ pytheory modes C                         # show all modes
$ pytheory circle C                        # circle of fifths
$ pytheory tune --instrument guitar        # strobe tuner, string-locked
$ pytheory studio                          # browser: recording → sheet music
$ pytheory live --link                     # MIDI synth rig, Ableton Link sync
```

Live MIDI input and Ableton Link sync are optional extras:

```
$ pip install "pytheory[live]"   # MIDI input (python-rtmidi)
$ pip install "pytheory[link]"   # Ableton Link sync
```

## Why Python?

A DAW is great for tweaking sounds. But when you're *thinking about music* — code is faster than clicking. Sketch ideas, hear them instantly, export MIDI, finish in your DAW.

Tools like [Claude Code](https://claude.ai/code) can use PyTheory to prototype musical ideas from natural language — "write a bossa nova in A minor with a saw lead and reverb" becomes real, playable music.

## Documentation

**[pytheory.org](https://pytheory.org)** — guides, API reference, and audio examples.

**[playground.kennethreitz.org](https://playground.kennethreitz.org)** — try PyTheory in your browser, nothing to install.
