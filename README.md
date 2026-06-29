<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kennethreitz/pytheory/master/ext/pytheory-small-dark.png">
    <img src="https://raw.githubusercontent.com/kennethreitz/pytheory/master/ext/pytheory-small.png" alt="PyTheory: music theory for humans" width="380">
  </picture>
</p>

<p align="center">
  <em>Explore music theory, compose multi-part arrangements, and hear them instantly — all in Python.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/pytheory/"><img src="https://img.shields.io/pypi/v/pytheory.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/pytheory/"><img src="https://img.shields.io/pypi/pyversions/pytheory.svg" alt="Python versions"></a>
  <a href="https://github.com/kennethreitz/pytheory/blob/master/LICENSE"><img src="https://img.shields.io/pypi/l/pytheory.svg" alt="License"></a>
</p>

<p align="center">
  <strong><a href="https://playground.pytheory.org">▶ Try it in your browser</a></strong> — a live demo of what PyTheory can do, nothing to install.
  <br>
  <a href="https://pytheory.org">Documentation</a> · <a href="https://pypi.org/project/pytheory/">PyPI</a> · <a href="https://pytheory.org/changelog.html">Changelog</a> · <a href="https://github.com/kennethreitz/pytheory-skill">Claude Skill</a>
</p>

---

```
$ pip install pytheory
$ pytheory demo        # hear a generated track right now
```

## Sketch Ideas Fast

```python
from pytheory import Score, Chord, Duration
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
e|--0--
B|--1--
G|--2--
D|--2--
A|--0--
E|--x--

>>> Fretboard.guitar().chord("G")
Fingering(E=3, A=2, D=0, G=0, B=0, e=3)
```

Melodies and basslines render to ASCII tablature with `part.to_tab()`,
and chord charts work in Nashville numbers too.

## Composition

Song structure with sections, repeats, and parameter automation:

```python
score = Score("4/4", bpm=124)
score.drums("house", repeats=16, fill="house", fill_every=8)

pad = score.part("pad", synth="supersaw", envelope="pad",
                 reverb=0.5, chorus=0.3, sidechain=0.85)
lead = score.part("lead", synth="saw", envelope="pluck",
                  legato=True, glide=0.03, humanize=0.3)
bass = score.part("bass", synth="sine", lowpass=300, sidechain=0.7)

score.section("verse")
# ... add notes ...
score.section("chorus")
lead.set(lowpass=5000, reverb=0.3)
# ... add notes ...
score.end_section()

score.repeat("verse")
score.repeat("chorus", times=2)
```

## Batteries Included

- **56 synth waveforms** — the 10 classics (sine, saw, triangle, square, pulse, FM, noise, supersaw, PWM) plus 46 modeled instruments: Rhodes, Wurlitzer, pipe organ, vibraphone, choir, sitar, theremin, and more.
- **100 drum patterns** — rock, jazz, bebop, bossa nova, salsa, samba, afrobeat, funk, reggae, house, trap, metal, drum and bass, and 87 more. 37 fill presets, 74 synthesized percussion sounds, stereo panned like a real kit.
- **6 effects with automation** — distortion, chorus, lowpass, delay, reverb, and LFO modulation on any parameter. Sidechain compression, master bus compressor/limiter, stereo output.
- **Convolution reverb** — 7 impulse responses: Taj Mahal (12s), cathedral, plate, spring, cave, parking garage, canyon.
- **6 musical systems** — Western, Indian (Hindustani), Arabic (Maqam), Japanese, Blues/Pentatonic, Javanese Gamelan. 40+ scales.
- **83 instrument presets** — guitar (8 tunings), bass, ukulele, mandolin family, violin family, banjo, harp, oud, sitar, erhu, and more.

```python
lead = score.part("lead", synth="saw",
                  distortion=0.7, lowpass=1000, lowpass_q=5.0,
                  delay=0.3, reverb=0.4, reverb_type="plate")

lead.set(lowpass=4000, distortion=0.9)                  # automate mid-song
lead.lfo("lowpass", rate=0.5, min=400, max=3000, bars=8)  # LFO modulation
```

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

## Talk to it with Claude

PyTheory ships an [official Claude Code plugin](https://github.com/kennethreitz/pytheory-skill) — six skills that let Claude compose, analyze, and notate music for you. In Claude Code:

```
/plugin marketplace add kennethreitz/pytheory-skill
/plugin install composing-with-pytheory@pytheory
```

Then just ask — *"write me a bossa nova in G minor"*, *"what's the fingering for F#m7b5?"*, *"turn this hum into a lead sheet"*. See the [guide](https://pytheory.org/guide/claude.html). For a real album made entirely in PyTheory, hear [Interpretations](https://interpretations.kennethreitz.org).

## Learn More

- **[playground.pytheory.org](https://playground.pytheory.org)** — try PyTheory in your browser, nothing to install.
- **[pytheory.org](https://pytheory.org)** — guides, API reference, and audio examples.
- **[pytheory-skill](https://github.com/kennethreitz/pytheory-skill)** — the official Claude Code plugin (six skills) to make music by talking to Claude.
- **[ableton-pytheory](https://github.com/kennethreitz/ableton-pytheory)** — drive Ableton Live from PyTheory, for those interested.
