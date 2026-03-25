Drums
=====

PyTheory includes a complete drum system — 27 synthesized percussion
sounds, 58 pattern presets across dozens of genres, and 21 fill presets.
Every sound is generated from waveforms; no samples needed.

Drum Sounds
-----------

The ``DrumSound`` enum maps to General MIDI percussion note numbers:

.. code-block:: pycon

   >>> from pytheory import DrumSound

   >>> DrumSound.KICK.value
   36
   >>> DrumSound.SNARE.value
   38
   >>> DrumSound.CLOSED_HAT.value
   42

All 27 sounds, organized by type:

**Kicks:** KICK (36)

**Snares:** SNARE (38), RIMSHOT (37), CLAP (39)

**Hi-hats:** CLOSED_HAT (42), OPEN_HAT (46), PEDAL_HAT (44)

**Toms:** LOW_TOM (45), MID_TOM (47), HIGH_TOM (50)

**Cymbals:** CRASH (49), RIDE (51), RIDE_BELL (53)

**Percussion:** COWBELL (56), CLAVE (75), SHAKER (70), TAMBOURINE (54),
CONGA_HIGH (63), CONGA_LOW (64), BONGO_HIGH (60), BONGO_LOW (61),
TIMBALE_HIGH (65), TIMBALE_LOW (66), AGOGO_HIGH (67), AGOGO_LOW (68),
GUIRO (73), MARACAS (70)

Drum Synthesis
--------------

Each sound has a dedicated synthesizer:

- **KICK** -- sine wave with pitch envelope sweep (150 to 50 Hz) + sub click
- **SNARE** -- pitched body (180 Hz) + white noise rattle
- **CLOSED_HAT** -- high-frequency noise, 50ms decay
- **OPEN_HAT** -- high-frequency noise, 250ms decay
- **CLAP** -- layered noise bursts with spacers
- **RIMSHOT** -- bright 800 Hz click + noise
- **TOMS** -- pitched sine with sweep (low=100, mid=150, high=200 Hz)
- **CRASH** -- long noise decay (1.5s)
- **RIDE** -- metallic ring (3500+5100 Hz) + noise
- **RIDE_BELL** -- brighter ring, more sustain
- **COWBELL** -- two detuned tones (545+815 Hz)
- **CLAVE** -- short 2500 Hz click
- **CONGAS/BONGOS** -- pitched membrane with slap transient
- **TIMBALES** -- bright metallic ring with overtones
- **AGOGO** -- pitched bell with harmonics
- **SHAKER/MARACAS** -- short noise burst
- **TAMBOURINE** -- noise + 7000 Hz jingle ring
- **GUIRO** -- scraped noise bursts

Pattern Presets
---------------

58 patterns spanning genres from rock to Afro-Cuban to electronic.
Load them with ``Pattern.preset()``:

.. code-block:: pycon

   >>> from pytheory import Pattern

   >>> Pattern.list_presets()
   ['12/8 blues', '6/8 afro-cuban', 'afrobeat', 'baiao', 'bebop', ...]

   >>> rock = Pattern.preset("rock")
   >>> rock
   <Pattern 'rock' 4/4 4.0 beats 12 hits>

**Rock/Pop:** rock, half time, double time, disco, motown, train beat

**Jazz:** jazz, bebop, shuffle, swing, linear, paradiddle

**Latin:** salsa, bossa nova, samba, cumbia, merengue, baiao, maracatu,
bolero, tango

**Afro-Cuban:** son clave 3-2, son clave 2-3, rumba clave 3-2,
rumba clave 2-3, cascara, guaguanco, mozambique, nanigo, bembe,
6/8 afro-cuban, tresillo, habanera

**African:** afrobeat, highlife

**Caribbean:** reggae, dancehall, ska, dub

**Electronic:** house, techno, trap, drum and bass, breakbeat, jungle

**Metal/Punk:** metal, blast beat, punk

**Other:** funk, hip hop, bo diddley, second line, new orleans, waltz,
12/8 blues, country, gospel, flamenco

Playing Patterns
----------------

``play_pattern()`` synthesizes every drum sound in real-time:

.. code-block:: pycon

   >>> from pytheory import Pattern
   >>> from pytheory.play import play_pattern

   >>> play_pattern(Pattern.preset("rock"), repeats=4, bpm=120)
   >>> play_pattern(Pattern.preset("bossa nova"), repeats=4, bpm=140)
   >>> play_pattern(Pattern.preset("salsa"), repeats=4, bpm=180)
   >>> play_pattern(Pattern.preset("afrobeat"), repeats=8, bpm=110)

Fills
-----

``Pattern.fill()`` loads a 1-bar drum fill — a short break that
transitions between sections. 21 fill presets are available:

.. code-block:: pycon

   >>> Pattern.list_fills()
   ['afrobeat', 'blast', 'bossa nova', 'breakdown', 'buildup',
    'cumbia', 'disco', 'funk', 'highlife', 'hip hop', 'house',
    'jazz', 'jazz brush', 'metal', 'reggae', 'rock', 'rock crash',
    'salsa', 'samba', 'second line', 'trap']

   >>> fill = Pattern.fill("rock")
   >>> fill
   <Pattern 'rock fill' 4/4 4.0 beats ...>

Score Integration
-----------------

The ``score.drums()`` shorthand attaches a drum pattern to a score:

.. code-block:: pycon

   >>> from pytheory import Score
   >>> score = Score("4/4", bpm=140)
   >>> score.drums("bossa nova", repeats=4)

Auto-Fills
~~~~~~~~~~

The ``fill`` and ``fill_every`` parameters automatically insert drum
fills at regular intervals:

.. code-block:: pycon

   >>> score = Score("4/4", bpm=120)
   >>> score.drums("rock", repeats=8, fill="rock", fill_every=4)

This plays the rock pattern for 8 bars, replacing every 4th bar with
a rock fill. Useful for adding natural phrasing to longer sections.

.. code-block:: pycon

   >>> # Jazz with brush fills every 8 bars
   >>> score.drums("bebop", repeats=16, fill="jazz brush", fill_every=8)

   >>> # Salsa with fills every 4 bars
   >>> score.drums("salsa", repeats=8, fill="salsa", fill_every=4)

Layering Patterns
-----------------

Combine drum patterns with melodic parts for full arrangements. The
drum pattern and all named parts are mixed together by ``play_score()``:

.. code-block:: pycon

   >>> from pytheory import Score, Key, Duration, Chord
   >>> from pytheory.play import play_score

   >>> score = Score("4/4", bpm=180)
   >>> score.drums("salsa", repeats=4, fill="salsa", fill_every=4)

   >>> pads = score.part("pads", synth="sine", envelope="pad", volume=0.3)
   >>> lead = score.part("lead", synth="saw", envelope="pluck", volume=0.4)
   >>> bass = score.part("bass", synth="sine", envelope="pluck", volume=0.45)

   >>> for chord in Key("D", "minor").progression("ii", "V", "i", "i") * 2:
   ...     pads.add(chord, Duration.WHOLE)

   >>> lead.add("A5", 0.67).add("G5", 0.33).add("F5", 0.67).add("E5", 0.33)

   >>> for n in ["D2", "A2", "D2", "F2"] * 2:
   ...     bass.add(n, Duration.QUARTER)

   >>> play_score(score)

MIDI Export
-----------

Convert any pattern to a Score, then export to MIDI (drums are written
to channel 10):

.. code-block:: pycon

   >>> pattern = Pattern.preset("bossa nova")
   >>> score = pattern.to_score(repeats=8, bpm=140)
   >>> score.save_midi("bossa.mid")

   >>> Pattern.preset("afrobeat").to_score(repeats=8, bpm=110).save_midi("afrobeat.mid")
