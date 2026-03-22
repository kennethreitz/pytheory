# PyTheory: Music Theory for Humans

This library makes exploring music theory approachable and fun, treating Python as a musical instrument.

## Installation

```
$ pip install pytheory
```

## Tones

```pycon
>>> from pytheory import Tone

>>> c4 = Tone.from_string("C4", system="western")
>>> c4.frequency
261.63

>>> c4 + 7                # perfect fifth
<Tone G4>

>>> c4.interval_to(c4 + 7)
'perfect 5th'

>>> c4.midi
60

>>> Tone.from_frequency(440)
<Tone A4>

>>> Tone.from_midi(69)
<Tone A4>
```

## Scales and Modes

```pycon
>>> from pytheory import TonedScale

>>> c_major = TonedScale(tonic="C4")["major"]
>>> c_major.note_names
['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']

>>> TonedScale(tonic="C4")["dorian"].note_names
['C', 'D', 'D#', 'F', 'G', 'A', 'A#', 'C']
```

## Diatonic Harmony

```pycon
>>> c_major.triad(0).identify()
'C major'

>>> c_major.seventh(4).identify()
'G dominant 7th'

>>> [c.identify() for c in c_major.harmonize()]
['C major', 'D minor', 'E minor', 'F major', 'G major', 'A minor', 'B diminished']

>>> [c.identify() for c in c_major.progression("I", "V", "vi", "IV")]
['C major', 'G major', 'A minor', 'F major']
```

## Chord Analysis

```pycon
>>> from pytheory import Chord, Tone

>>> C4 = Tone.from_string("C4", system="western")
>>> G4 = Tone.from_string("G4", system="western")

>>> g7 = Chord([G4, G4+4, G4+7, G4+10])
>>> g7.identify()
'G dominant 7th'

>>> g7.analyze("C")
'V7'

>>> g7.tension
{'score': 0.6, 'tritones': 1, 'minor_seconds': 0, 'has_dominant_function': True}

>>> g7.transpose(-7).identify()
'C dominant 7th'
```

## Six Musical Systems

```pycon
>>> from pytheory import TonedScale
>>> from pytheory.systems import SYSTEMS

>>> TonedScale(tonic="Sa4", system=SYSTEMS["indian"])["bhairav"].note_names
['Sa', 'komal Re', 'Ga', 'Ma', 'Pa', 'komal Dha', 'Ni', 'Sa']

>>> TonedScale(tonic="Do4", system=SYSTEMS["arabic"])["hijaz"].note_names
['Do', 'Reb', 'Mi', 'Fa', 'Sol', 'Solb', 'Sib', 'Do']

>>> TonedScale(tonic="C4", system=SYSTEMS["japanese"])["hirajoshi"].note_names
['C', 'D', 'D#', 'G', 'G#', 'C']

>>> TonedScale(tonic="C4", system=SYSTEMS["blues"])["blues"].note_names
['C', 'D#', 'F', 'F#', 'G', 'A#', 'C']
```

## 25 Instrument Presets

```pycon
>>> from pytheory import Fretboard, CHARTS

>>> Fretboard.guitar()                # standard tuning
>>> Fretboard.guitar("drop d")        # 8 alternate tunings
>>> Fretboard.mandolin()              # + mandola, octave mandolin, mandocello
>>> Fretboard.violin()                # + viola, cello, double bass
>>> Fretboard.ukulele()               # + banjo, harp, charango, erhu...
>>> Fretboard.keyboard()              # 88-key piano
>>> Fretboard.keyboard(25, "C3")      # 25-key MIDI controller

>>> CHARTS['western']['Am'].fingering(fretboard=Fretboard.guitar())
(0, 1, 2, 2, 0, 0)
```

## Audio Playback

```pycon
>>> from pytheory import play, Synth, Tone

>>> tone = Tone.from_string("A4", system="western")
>>> play(tone, t=1_000)                   # sine wave, 1 second
>>> play(tone, synth=Synth.SAW, t=1_000)  # sawtooth wave
```

## Features

- **6 musical systems**: Western, Indian (Hindustani), Arabic (Maqam), Japanese, Blues/Pentatonic, Javanese Gamelan
- **40+ scales**: major, minor, harmonic minor, 7 modes, 10 thaats, 10 maqamat, pentatonic, blues, hirajoshi, pelog, slendro, and more
- **Chord analysis**: identification (17 types), Roman numeral analysis, tension scoring, voice leading, Plomp-Levelt dissonance, beat frequencies
- **Diatonic harmony**: triads, seventh chords, harmonize entire scales, build progressions from Roman numerals
- **25 instrument presets**: guitar (8 tunings), 12-string, bass, mandolin family, violin family, banjo, harp, oud, sitar, shamisen, erhu, charango, pipa, balalaika, lute, pedal steel, keyboard
- **Pitch tools**: frequency ↔ tone conversion, MIDI ↔ tone, interval naming, circle of fifths, overtone series, transposition
- **3 temperaments**: equal, Pythagorean, quarter-comma meantone
- **Audio synthesis**: sine, sawtooth, and triangle wave playback

## Documentation

Full documentation with music theory guides: **[pytheory.kennethreitz.org](https://pytheory.kennethreitz.org)**
