# PyTheory: Music Theory for Humans

This library makes exploring music theory approachable and fun, treating Python as a musical instrument.

![logo](https://github.com/kennethreitz/pytheory/raw/master/ext/pytheory-small.png)

## Installation

```
$ pip install pytheory
```

## Scales and Modes

```pycon
>>> from pytheory import TonedScale

>>> c_major = TonedScale(tonic='C4')['major']
>>> c_major.note_names
['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']

>>> c_major.triad(0)    # I chord
<Chord tones=('C4', 'E4', 'G4')>

>>> c_major.triad(4)    # V chord
<Chord tones=('G4', 'B4', 'D5')>
```

## Tone Arithmetic

```pycon
>>> from pytheory import Tone

>>> c4 = Tone.from_string("C4", system="western")
>>> c4 + 7              # perfect fifth up
<Tone G4>

>>> c4.frequency
261.63

>>> (c4 + 12).frequency   # octave doubles frequency
523.25
```

## Chord Identification and Analysis

```pycon
>>> from pytheory import Chord, Tone

>>> c_maj = Chord([Tone.from_string(n, system="western") for n in ["C4", "E4", "G4"]])
>>> c_maj.identify()
'C major'

>>> c_maj.analyze("C")   # Roman numeral analysis
'I'

>>> g7 = Chord([Tone.from_string(n, system="western") for n in ["G4", "B4", "D5", "F5"]])
>>> g7.identify()
'G dominant 7th'

>>> g7.analyze("C")
'V7'

>>> g7.tension
{'score': 0.6, 'tritones': 1, 'minor_seconds': 0, 'has_dominant_function': True}
```

## Six Musical Systems

```pycon
>>> from pytheory.systems import SYSTEMS

>>> # Indian classical — 10 thaats
>>> TonedScale(tonic="Sa4", system=SYSTEMS["indian"])["bhairav"].note_names
['Sa', 'komal Re', 'Ga', 'Ma', 'Pa', 'komal Dha', 'Ni', 'Sa']

>>> # Arabic maqam
>>> TonedScale(tonic="Do4", system=SYSTEMS["arabic"])["hijaz"].note_names
['Do', 'Reb', 'Mi', 'Fa', 'Sol', 'Solb', 'Sib', 'Do']

>>> # Japanese pentatonic
>>> TonedScale(tonic="C4", system=SYSTEMS["japanese"])["hirajoshi"].note_names
['C', 'D', 'D#', 'G', 'G#', 'C']

>>> # Blues
>>> TonedScale(tonic="C4", system=SYSTEMS["blues"])["blues"].note_names
['C', 'D#', 'F', 'F#', 'G', 'A#', 'C']
```

## Guitar Chord Fingerings

```pycon
>>> from pytheory import Fretboard, CHARTS

>>> fb = Fretboard.guitar()               # standard tuning
>>> fb = Fretboard.guitar("drop d")       # or any alternate tuning

>>> CHARTS['western']['C'].fingering(fretboard=fb)
(0, 1, 0, 2, 3, 0)

>>> CHARTS['western']['Am'].fingering(fretboard=fb)
(0, 1, 2, 2, 0, 0)
```

## Audio Playback

```pycon
>>> from pytheory import play, Synth, Tone

>>> tone = Tone.from_string("A4", system="western")
>>> play(tone, t=1_000)                   # sine wave, 1 second
>>> play(tone, synth=Synth.SAW, t=1_000)  # sawtooth wave
```

## Documentation

Full documentation with music theory guides: [pytheory.kennethreitz.org](https://pytheory.kennethreitz.org)
