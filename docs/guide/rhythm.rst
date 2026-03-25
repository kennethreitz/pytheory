Sequencing: Rhythm and Scores
=============================

The rhythm module lets you pair tones and chords with durations,
organize them into measures, and export measure-aware MIDI files.

Duration
--------

A ``Duration`` represents a note length in beats (quarter note = 1 beat):

.. code-block:: pycon

   >>> from pytheory import Duration

   >>> Duration.WHOLE.value
   4.0
   >>> Duration.HALF.value
   2.0
   >>> Duration.QUARTER.value
   1.0
   >>> Duration.EIGHTH.value
   0.5
   >>> Duration.SIXTEENTH.value
   0.25
   >>> Duration.DOTTED_HALF.value
   3.0
   >>> Duration.DOTTED_QUARTER.value
   1.5
   >>> Duration.TRIPLET_QUARTER.value    # 2/3 of a beat
   0.6666666666666666

Time Signatures
---------------

A ``TimeSignature`` holds the meter of a piece — how many beats per
measure and which note value gets one beat:

.. code-block:: pycon

   >>> from pytheory.rhythm import TimeSignature

   >>> ts = TimeSignature.from_string("4/4")
   >>> ts.beats_per_measure
   4.0

   >>> TimeSignature.from_string("3/4").beats_per_measure
   3.0

   >>> TimeSignature.from_string("6/8").beats_per_measure
   3.0

   >>> TimeSignature.from_string("12/8").beats_per_measure
   6.0

The ``beats_per_measure`` is always in quarter-note units. In 6/8,
there are 6 eighth notes per bar = 3 quarter-note beats.

Building a Score
----------------

A ``Score`` is a sequence of notes and rests with a time signature and
tempo. Use ``.add()`` and ``.rest()`` for fluent chaining:

.. code-block:: pycon

   >>> from pytheory import Score, Duration, Tone

   >>> score = Score("4/4", bpm=120)
   >>> score.add(Tone.from_string("C4", system="western"), Duration.QUARTER)
   <Score 4/4 120bpm ...>
   >>> score.add(Tone.from_string("E4", system="western"), Duration.QUARTER)
   <Score 4/4 120bpm ...>
   >>> score.add(Tone.from_string("G4", system="western"), Duration.HALF)
   <Score 4/4 120bpm ...>

   >>> score.total_beats
   4.0
   >>> score.measures
   1.0
   >>> score.duration_ms
   2000.0

Rests
~~~~~

Add silence with ``.rest()`` or the ``Rest()`` helper:

.. code-block:: pycon

   >>> score = Score("4/4", bpm=120)
   >>> score.add(Tone.from_string("C4", system="western"), Duration.HALF)
   <Score 4/4 120bpm ...>
   >>> score.rest(Duration.HALF)
   <Score 4/4 120bpm ...>
   >>> score.measures
   1.0

Chords with Rhythm
~~~~~~~~~~~~~~~~~~

Chords work just like tones — pass any ``Chord`` object:

.. code-block:: pycon

   >>> from pytheory import Score, Duration, Key

   >>> key = Key("C", "major")
   >>> chords = key.progression("I", "V", "vi", "IV")

   >>> score = Score("4/4", bpm=120)
   >>> for chord in chords:
   ...     score.add(chord, Duration.WHOLE)

   >>> score.measures
   4.0
   >>> score.duration_ms
   8000.0

Compound Time
~~~~~~~~~~~~~

12/8 is a compound meter — 12 eighth notes per bar grouped in four
groups of three. Each group feels like one "big beat":

.. code-block:: pycon

   >>> from pytheory import Score, Duration, Key

   >>> key = Key("A", "minor")
   >>> chords = key.random_progression(4)

   >>> score = Score("12/8", bpm=120)
   >>> for c in chords:
   ...     # Two dotted halves = one bar of 12/8
   ...     score.add(c, Duration.DOTTED_HALF)
   ...     score.add(c, Duration.DOTTED_HALF)

   >>> score.measures
   4.0

MIDI Export
-----------

``Score.save_midi()`` writes a Standard MIDI File with proper time
signature and tempo meta events:

.. code-block:: pycon

   >>> from pytheory import Score, Duration, Key

   >>> key = Key("G", "major")
   >>> score = Score("4/4", bpm=140)
   >>> for chord in key.progression("I", "IV", "V", "I"):
   ...     score.add(chord, Duration.WHOLE)
   >>> score.save_midi("progression.mid")

The MIDI file can be opened in any DAW (Logic, Ableton, GarageBand,
Reaper, etc.), notation software (MuseScore, Sibelius), or MIDI player.

Drum Patterns
=============

PyTheory includes 48 drum pattern presets spanning genres from rock to
Afro-Cuban to electronic. Each pattern is defined as a set of hits at
specific beat positions, using General MIDI percussion sounds.

Listing Presets
---------------

.. code-block:: pycon

   >>> from pytheory import Pattern
   >>> Pattern.list_presets()
   ['12/8 blues', '6/8 afro-cuban', 'afrobeat', 'baiao', 'bebop', ...]

Loading a Pattern
-----------------

.. code-block:: pycon

   >>> rock = Pattern.preset("rock")
   >>> rock
   <Pattern 'rock' 4/4 4.0 beats 12 hits>

   >>> salsa = Pattern.preset("salsa")
   >>> salsa
   <Pattern 'salsa' 4/4 8.0 beats 29 hits>

   >>> bebop = Pattern.preset("bebop")
   >>> waltz = Pattern.preset("waltz")

Available Genres
~~~~~~~~~~~~~~~~

**Rock/Pop**: rock, half time, double time, disco, motown, train beat

**Jazz**: jazz, bebop, shuffle, linear, paradiddle

**Latin**: salsa, bossa nova, samba, cumbia, merengue, baiao, maracatu

**Afro-Cuban**: son clave 3-2, son clave 2-3, rumba clave 3-2, rumba clave 2-3,
cascara, guaguanco, mozambique, nanigo, bembe, 6/8 afro-cuban, tresillo, habanera

**African**: afrobeat, highlife

**Caribbean**: reggae, dancehall

**Electronic**: house, trap, drum and bass, breakbeat

**Metal/Punk**: metal, blast beat, punk

**Other**: funk, hip hop, bo diddley, second line, new orleans, waltz, 12/8 blues

Exporting to MIDI
-----------------

Convert any pattern to a Score, then export:

.. code-block:: pycon

   >>> pattern = Pattern.preset("bossa nova")
   >>> score = pattern.to_score(repeats=8, bpm=140)
   >>> score.save_midi("bossa.mid")

   >>> Pattern.preset("salsa").to_score(repeats=4, bpm=180).save_midi("salsa.mid")
   >>> Pattern.preset("afrobeat").to_score(repeats=8, bpm=110).save_midi("afrobeat.mid")

Multi-Part Arrangements
-----------------------

The ``Part`` class lets you layer multiple instrument voices — each with
its own synth waveform, ADSR envelope, and volume level. This is where
PyTheory goes from "theory tool" to "composition tool."

Create parts with ``Score.part()``:

.. code-block:: pycon

   >>> from pytheory import Score, Pattern, Key, Duration, Chord
   >>> from pytheory.play import play_score

   >>> score = Score("4/4", bpm=140)
   >>> score.drums("bossa nova", repeats=4)

   >>> chords = score.part("chords", synth="sine", envelope="pad", volume=0.35)
   >>> lead   = score.part("lead",   synth="saw",  envelope="pluck", volume=0.5)
   >>> bass   = score.part("bass",   synth="triangle", envelope="pluck", volume=0.45)

Each part has ``.add()`` and ``.rest()`` with fluent chaining. Parts accept
note strings directly — no need to wrap in ``Tone.from_string()``:

.. code-block:: pycon

   >>> lead.add("E5", Duration.QUARTER).add("D5", Duration.EIGHTH).rest(Duration.EIGHTH)
   <Part 'lead' ...>

   >>> # Raw float beats work too — useful for swing and tuplets
   >>> lead.add("C5", 0.67).add("B4", 0.33).add("A4", 1.0)
   <Part 'lead' ...>

Chords and Tone objects work the same way:

.. code-block:: pycon

   >>> for chord in Key("A", "minor").progression("i", "iv", "V", "i"):
   ...     chords.add(chord, Duration.WHOLE)

   >>> for note in ["A2", "C3", "E3", "A2", "D2", "F2", "A2", "D2"]:
   ...     bass.add(note, Duration.QUARTER)

   >>> play_score(score)

Available Synths and Envelopes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Synths** (10 waveforms):

=============  ================================================
Name           Character
=============  ================================================
``"sine"``     Pure tone, no harmonics — clean pads, sub bass
``"saw"``      All harmonics — bright, buzzy leads and brass
``"triangle"`` Odd harmonics at 1/n² — mellow, woody, flute-like
``"square"``   Odd harmonics at 1/n — hollow, chiptune, 8-bit
``"pulse"``    Variable duty cycle — nasal, NES-style
``"fm"``       Frequency modulation — bells, e-piano, metallic (DX7)
``"noise"``    White noise — percussion, wind, texture
``"supersaw"`` 7 detuned saws — fat, shimmery trance/EDM pads
``"pwm_slow"`` Pulse width modulation, slow LFO — lush Juno pads
``"pwm_fast"`` Pulse width modulation, fast LFO — chorus/vibrato
=============  ================================================

**Envelopes** (8 presets):

===============  ================================================
Name             Character
===============  ================================================
``"piano"``      Quick attack, natural decay
``"pluck"``      Sharp attack, fast decay
``"pad"``        Slow fade in, lush sustain
``"organ"``      Instant on/off
``"bell"``       Instant attack, long ring
``"strings"``    Gradual bow attack
``"staccato"``   Short and punchy
``"none"``       Raw waveform, no shaping
===============  ================================================

**Effects** (per-part, set at creation):

======================  ================================================
Parameter               Description
======================  ================================================
``reverb``              Wet/dry mix 0–1 (default 0, off)
``reverb_decay``        Tail length in seconds (default 1.0)
``delay``               Wet/dry mix 0–1 (default 0, off)
``delay_time``          Echo time in seconds (default 0.375)
``delay_feedback``      Echo feedback 0–1 (default 0.4)
``lowpass``             Cutoff in Hz (default 0, off)
``lowpass_q``           Resonance Q (default 0.707, flat)
``distortion``          Wet/dry mix 0–1 (default 0, off)
``distortion_drive``    Gain before clipping (default 3.0)
======================  ================================================

Signal chain: distortion → lowpass → delay → reverb.

Legato and Glide
~~~~~~~~~~~~~~~~

By default, each note gets its own attack/release envelope. ``legato=True``
renders the entire part as one continuous waveform — the pitch changes
at note boundaries but the envelope flows unbroken. Add ``glide`` for
portamento (pitch slides between notes):

.. code-block:: pycon

   >>> acid = score.part("acid", synth="saw", envelope="pad",
   ...                   legato=True, glide=0.04)
   >>> acid.add("C2", 0.25).add("C3", 0.25).add("G2", 0.25).add("C2", 0.25)

- ``legato``: If True, no envelope retrigger between notes (default False).
- ``glide``: Portamento time in seconds (default 0, instant).
  0.03–0.05 = quick 303 slide, 0.1–0.2 = slow glide.

Arpeggiator
~~~~~~~~~~~

``Part.arpeggio()`` takes a chord and sequences through its notes
automatically — like a hardware arpeggiator on a synth:

.. code-block:: pycon

   >>> lead = score.part("lead", synth="saw", legato=True, glide=0.03,
   ...                   distortion=0.8, lowpass=1000, lowpass_q=5.0)
   >>> lead.arpeggio(Chord.from_symbol("Cm"), bars=2, pattern="up",
   ...              division=Duration.SIXTEENTH, octaves=2)

Parameters:

- ``chord``: A Chord object or string like ``"Am"``.
- ``bars``: Number of bars to fill (default 1).
- ``pattern``: ``"up"``, ``"down"``, ``"updown"``, ``"downup"``, ``"random"``.
- ``division``: Step length (default ``Duration.SIXTEENTH``).
- ``octaves``: Octave span (default 1). With 2, pattern repeats one octave up.

Chain arpeggios for chord progressions:

.. code-block:: pycon

   >>> for sym in ["Cm", "Fm", "Abm", "Gm"]:
   ...     lead.arpeggio(sym, bars=2, pattern="updown", octaves=2)

Combined with legato, glide, distortion, and a resonant lowpass, this
produces the classic acid/trance arpeggiator sound.

Full Example: Bossa Nova with Effects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A complete arrangement with drums, chord pads, walking bass, melody,
and per-part effects:

.. code-block:: pycon

   >>> from pytheory import Score, Pattern, Key, Duration, Chord
   >>> from pytheory.play import play_score

   >>> score = Score("4/4", bpm=140)
   >>> score.drums("bossa nova", repeats=4)

   >>> # FM rhodes with reverb — jazz club warmth
   >>> rhodes = score.part("rhodes", synth="fm", envelope="piano",
   ...                     volume=0.3, reverb=0.4, reverb_decay=1.8)

   >>> # Triangle lead with delay — echoes that bloom
   >>> lead = score.part("lead", synth="triangle", envelope="pluck",
   ...                   volume=0.45, delay=0.25, delay_time=0.32,
   ...                   delay_feedback=0.35, reverb=0.2)

   >>> # Filtered bass — warm and round
   >>> bass = score.part("bass", synth="sine", envelope="pluck",
   ...                   volume=0.45, lowpass=600)

   >>> for sym in ["Am", "Am", "Dm", "Dm", "E7", "E7", "Am", "Am"]:
   ...     rhodes.add(Chord.from_symbol(sym), Duration.WHOLE)

   >>> for n, d in [("E5",.67),("D5",.33),("C5",.67),("B4",.33),
   ...              ("A4",1),("C5",.67),("E5",.33),("D5",.67),("C5",.33),
   ...              ("A4",1)]:
   ...     lead.add(n, d)

   >>> for n in ["A2","E2","A2","C3","D2","A2","D2","F2"]:
   ...     bass.add(n, Duration.QUARTER)

   >>> play_score(score)

Headless Rendering
~~~~~~~~~~~~~~~~~~

Use ``render_score()`` to get a raw audio buffer without playing it —
useful for saving to WAV or further processing:

.. code-block:: pycon

   >>> from pytheory.play import render_score
   >>> buf = render_score(score)   # numpy float32 array
   >>> len(buf)
   604800

Combining with MIDI Export
~~~~~~~~~~~~~~~~~~~~~~~~~~

Scores with parts can also be exported to MIDI (parts are rendered
to the default channel, drums to channel 10):

.. code-block:: pycon

   >>> score.save_midi("bossa_arrangement.mid")

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
   >>> DrumSound.RIDE.value
   51
   >>> DrumSound.CLAVE.value
   75
   >>> DrumSound.CONGA_HIGH.value
   63

Available sounds: KICK, SNARE, RIMSHOT, CLAP, CLOSED_HAT, OPEN_HAT,
PEDAL_HAT, LOW_TOM, MID_TOM, HIGH_TOM, CRASH, RIDE, RIDE_BELL, COWBELL,
CLAVE, SHAKER, TAMBOURINE, CONGA_HIGH, CONGA_LOW, BONGO_HIGH, BONGO_LOW,
TIMBALE_HIGH, TIMBALE_LOW, AGOGO_HIGH, AGOGO_LOW, GUIRO, MARACAS.

Playing Drum Patterns
=====================

``play_pattern()`` synthesizes every drum sound in real-time — kicks
have pitch sweeps, snares have noise rattles, hats are filtered noise,
congas have membrane resonance, and so on. No samples or external
files needed.

.. code-block:: pycon

   >>> from pytheory import Pattern
   >>> from pytheory.play import play_pattern

   >>> play_pattern(Pattern.preset("rock"), repeats=4, bpm=120)
   >>> play_pattern(Pattern.preset("bossa nova"), repeats=4, bpm=140)
   >>> play_pattern(Pattern.preset("salsa"), repeats=4, bpm=180)
   >>> play_pattern(Pattern.preset("afrobeat"), repeats=8, bpm=110)

Playing Drums with Parts
-------------------------

``play_score()`` mixes drums and all named parts together. Use
``Score.part()`` to create voices with different timbres:

.. code-block:: pycon

   >>> from pytheory import Score, Pattern, Key, Duration, Chord
   >>> from pytheory.play import play_score

   >>> score = Score("4/4", bpm=140)
   >>> score.drums("bossa nova", repeats=4)

   >>> chords = score.part("chords", synth="sine", envelope="pad", volume=0.3)
   >>> lead = score.part("lead", synth="triangle", envelope="pluck", volume=0.5)

   >>> for chord in Key("A", "minor").progression("i", "iv", "V", "i"):
   ...     chords.add(chord, Duration.WHOLE)

   >>> lead.add("E5", 0.67).add("D5", 0.33).add("C5", 1.0).rest(1.0)

   >>> play_score(score)

Another example — salsa with a saw lead and walking bass:

.. code-block:: pycon

   >>> score = Score("4/4", bpm=180)
   >>> score.drums("salsa", repeats=4)
   >>> pads = score.part("pads", synth="sine", envelope="pad", volume=0.3)
   >>> lead = score.part("lead", synth="saw", envelope="pluck", volume=0.4)
   >>> bass = score.part("bass", synth="sine", envelope="pluck", volume=0.45)
   >>> for chord in Key("D", "minor").progression("ii", "V", "i", "i") * 2:
   ...     pads.add(chord, Duration.WHOLE)
   >>> lead.add("A5", 0.67).add("G5", 0.33).add("F5", 0.67).add("E5", 0.33)
   >>> for n in ["D2", "A2", "D2", "F2"] * 2:
   ...     bass.add(n, Duration.QUARTER)
   >>> play_score(score)

Synthesized Drum Sounds
-----------------------

Each ``DrumSound`` has a dedicated synthesizer:

- **KICK** — sine wave with pitch envelope sweep (150→50 Hz) + sub click
- **SNARE** — pitched body (180 Hz) + white noise rattle
- **CLOSED_HAT** — high-frequency noise, 50ms decay
- **OPEN_HAT** — high-frequency noise, 250ms decay
- **CLAP** — layered noise bursts with spacers
- **RIMSHOT** — bright 800 Hz click + noise
- **TOMS** — pitched sine with sweep (low=100, mid=150, high=200 Hz)
- **CRASH** — long noise decay (1.5s)
- **RIDE** — metallic ring (3500+5100 Hz) + noise
- **RIDE_BELL** — brighter ring, more sustain
- **COWBELL** — two detuned tones (545+815 Hz)
- **CLAVE** — short 2500 Hz click
- **CONGAS/BONGOS** — pitched membrane with slap transient
- **TIMBALES** — bright metallic ring with overtones
- **AGOGO** — pitched bell with harmonics
- **SHAKER/MARACAS** — short noise burst
- **TAMBOURINE** — noise + 7000 Hz jingle ring
- **GUIRO** — scraped noise bursts
