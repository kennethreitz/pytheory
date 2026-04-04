Synthesizers
============

PyTheory includes 56 built-in waveforms and 10 ADSR envelope presets.
Every sound is generated from scratch -- no samples or external audio
files needed.

Here's the beautiful thing about synthesis: all of it comes from math.
Sine waves, addition, and shaping. That's the entire foundation. Every
legendary synth in history -- the Moog Minimoog, the Sequential Prophet-5,
the Yamaha DX7, the Roland Juno-106, the Roland TB-303 -- uses some
combination of these building blocks. When you choose a waveform in
PyTheory, you're reaching for the same raw materials that defined
decades of music. The difference between a Moog bass and a DX7 bell
isn't magic; it's which waveforms you start with and how you shape them.

Classic Waveforms
-----------------

These four are the fundamentals. Every analog synthesizer ever built
starts here. If you learn nothing else about synthesis, learn these --
they're the primary colors you mix everything else from.

Sine
~~~~

The purest tone possible. Contains only the fundamental frequency with
no harmonics. Sounds smooth, clean, and "electronic." This is the
building block of all other waveforms (Fourier's theorem).

**Use for:** sub bass, clean pads, test tones, blending under other voices.

.. code-block:: python

   from pytheory import play, Synth, Tone

   tone = Tone.from_string("C4", system="western")
   play(tone, synth=Synth.SINE)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_sine.wav" type="audio/wav"></audio>

Sawtooth
~~~~~~~~

Contains all harmonics (both odd and even), each at amplitude 1/n.
The richest of the classic waveforms — bright, buzzy, and aggressive.
Named for its ramp shape.

**Use for:** leads, brass, pads, anything that needs presence and bite.

.. code-block:: python

   play(tone, synth=Synth.SAW)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_saw.wav" type="audio/wav"></audio>

Triangle
~~~~~~~~

Contains only odd harmonics, each at amplitude 1/n-squared. Softer and
more mellow than sawtooth — somewhere between sine and saw. Often
described as "woody" or "hollow."

**Use for:** flute-like leads, mellow bass, gentle pads.

.. code-block:: python

   play(tone, synth=Synth.TRIANGLE)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_triangle.wav" type="audio/wav"></audio>

Square
~~~~~~

Contains only odd harmonics, each at amplitude 1/n. Sounds hollow and
punchy — the classic chiptune / 8-bit sound. A special case of the
pulse wave with a 50% duty cycle.

**Use for:** chiptune, 8-bit game music, hollow leads, sub-octave bass.

.. code-block:: python

   play(tone, synth=Synth.SQUARE)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_square.wav" type="audio/wav"></audio>

Extended Waveforms
------------------

These go beyond the basics into territory that defined specific
instruments and eras. The pulse wave is the sound of the NES. FM
synthesis is the sound of the 1980s. If the classic waveforms are
primary colors, these are the specific pigments that painters actually
reach for.

Pulse
~~~~~

A pulse wave with a variable duty cycle. Narrower pulses sound thinner
and more nasal. At 50% it equals a square wave; at 10--20% it produces
the classic NES-style buzzy tone.

**Use for:** NES/chiptune sounds, nasal leads, retro textures.

.. code-block:: python

   lead = score.part("lead", synth="pulse", envelope="pluck")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_pulse.wav" type="audio/wav"></audio>

FM Synthesis
~~~~~~~~~~~~

Frequency modulation -- one oscillator (the modulator) modulates the
frequency of another (the carrier), producing complex inharmonic
spectra. This is how the Yamaha DX7 works -- the best-selling
synthesizer of all time. Released in 1983, it was suddenly everywhere:
the electric piano in every Whitney Houston ballad, the bass in every
Depeche Mode track, the bells in a thousand TV jingles. If you heard
pop music in the 80s, you heard FM synthesis.

**Use for:** bells, metallic leads, glassy pads, DX7-style sounds.

.. code-block:: python

   bells = score.part(
       "bells",
       synth="fm",
       envelope="bell",
       fm_ratio=3.0,
       fm_index=5.0,
       volume=0.3,
       reverb=0.4,
   )

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_fm.wav" type="audio/wav"></audio>

Noise
-----

White Noise
~~~~~~~~~~~

Equal energy at all frequencies — pure randomness with no pitch.
Useful as a texture layer, a percussion source, or a wind/ocean effect.

**Use for:** snare layers, hi-hats, wind effects, risers, ambient texture.

.. code-block:: python

   texture = score.part(
       "texture",
       synth="noise",
       envelope="pad",
       volume=0.1,
       lowpass=2000,
   )

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_noise.wav" type="audio/wav"></audio>

Ensemble Waveforms
------------------

These all create "bigger" sounds by layering or modulating multiple
oscillators. Where a single sawtooth wave sounds like one instrument,
these sound like a section -- a string ensemble, a choir, a wall of
synths. They're the pad and atmosphere machines, the sounds that fill
out a mix and make it feel wide and immersive.

Supersaw
~~~~~~~~

Seven detuned sawtooth oscillators stacked together. The slight pitch
differences create a shimmering, massive wall of sound. This is the
Roland JP-8000's gift to the world -- the waveform that launched an
entire genre. Every trance anthem from the late 90s and early 2000s,
every euphoric EDM drop, every J-pop power chord owes something to the
supersaw.

**Use for:** trance pads, EDM leads, massive chords, anthem hooks.

.. code-block:: python

   pad = score.part(
       "pad",
       synth="supersaw",
       envelope="pad",
       volume=0.4,
       chorus=0.3,
       reverb=0.5,
   )

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_supersaw.wav" type="audio/wav"></audio>

PWM Slow
~~~~~~~~

Pulse width modulation with a slow LFO. The duty cycle sweeps back and
forth, creating a lush, animated pad sound. This is the Roland Juno-106
in a nutshell -- arguably the most recorded synth pad sound in history.
That warm, slowly evolving, slightly chorused wash you hear in everything
from Boards of Canada to Drake? PWM with a slow LFO.

**Use for:** lush analog pads, slow evolving textures, Juno-style warmth.

.. code-block:: python

   pad = score.part(
       "pad",
       synth="pwm_slow",
       envelope="pad",
       volume=0.35,
       reverb=0.4,
   )

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_pwm_slow.wav" type="audio/wav"></audio>

PWM Fast
~~~~~~~~

Pulse width modulation with a fast LFO. The rapid duty cycle sweep
produces a natural chorus/vibrato effect built into the waveform itself.

**Use for:** animated leads, vibrato textures, movement without effects.

.. code-block:: python

   lead = score.part("lead", synth="pwm_fast", envelope="pluck", volume=0.5)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_pwm_fast.wav" type="audio/wav"></audio>

Analog Synthesis
----------------

These waveforms model the behavior of real analog hardware — the
imperfections, interactions, and nonlinearities that make a room full
of vintage synths sound so much more alive than a room full of VSTs.
Each one is a different approach to the same question: how do you make
a digital oscillator sound like it has a soul?

Hard Sync
~~~~~~~~~

A "slave" oscillator is forced to restart its cycle every time a
"master" oscillator completes one. The abrupt restart creates bright
formant peaks that sweep as the slave ratio changes. This is THE sound
of the Prophet-5, Moog Prodigy, and every screaming analog lead since
1978.

**Use for:** aggressive leads, formant sweeps, cutting solos.

.. code-block:: python

   lead = score.part("lead", synth="hard_sync", envelope="pluck")

   # Higher slave ratio = more harmonics, brighter
   from pytheory import play, Synth, Tone
   play(Tone.from_string("C4"), synth=Synth.HARD_SYNC, slave_ratio=2.5)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_hard_sync.wav" type="audio/wav"></audio>

Ring Modulation
~~~~~~~~~~~~~~~

Two oscillators multiplied together, producing sum and difference
frequencies. Unlike FM, ring mod outputs only sidebands — no carrier
or modulator fundamental. The result is metallic, bell-like, and often
inharmonic. Classic Dalek voice, Stockhausen, and every sci-fi
soundtrack.

**Use for:** metallic bells, alien textures, inharmonic percussion.

.. code-block:: python

   bells = score.part("bells", instrument="ring_mod_bell",
                      reverb=0.5, reverb_type="cave")

   # Non-integer ratios = more inharmonic
   play(Tone.from_string("C4"), synth=Synth.RING_MOD, mod_ratio=2.1)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_ring_mod.wav" type="audio/wav"></audio>

Wavefolding
~~~~~~~~~~~

The heart of west coast synthesis (Buchla, Make Noise, Verbos). A sine
wave is amplified past ±1.0, then "folded" — the overflow bounces back
instead of clipping. Each fold adds new harmonic pairs. At low fold
counts it's warm and round; crank it up and it gets buzzy, gnarly, and
alive.

This sounds completely different from subtractive synthesis — instead of
*removing* harmonics with a filter, you're *generating* them by shaping
the wave. Pairs beautifully with a lowpass filter after the fold.

**Use for:** complex leads, evolving textures, west coast basslines.

.. code-block:: python

   # Warm, musical folding
   warm = score.part("fold", instrument="wavefold_warm")

   # Cranked and aggressive
   gnarly = score.part("gnarly", instrument="wavefold_gnarly")

   # Direct control over fold amount
   play(Tone.from_string("C4"), synth=Synth.WAVEFOLD, folds=3.0)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_wavefold.wav" type="audio/wav"></audio>

Drift Oscillator
~~~~~~~~~~~~~~~~

Real analog oscillators are never perfectly stable. Capacitor charging,
thermal variations, and component tolerances make the pitch wander
slightly. This is what makes a Minimoog sound "fat" and a VST sound
"thin" — the constant micro-motion of imperfect hardware.

The drift oscillator models slow pitch drift (< 1 Hz wander), fast
jitter (per-cycle randomness), a soft analog noise floor, and slightly
rounded waveform edges. It turns any basic shape into something that
breathes.

**Use for:** analog-style pads, warm basses, vintage leads, any voice
that needs to feel "alive."

.. code-block:: python

   # Vintage Minimoog-style saw
   pad = score.part("pad", instrument="drift_saw",
                    reverb=0.35, reverb_type="taj_mahal")

   # Hollow square with analog wobble
   sq = score.part("sq", instrument="drift_square")

   # Control the shape and instability directly
   play(Tone.from_string("C4"), synth=Synth.DRIFT,
        shape="triangle", drift_amount=0.25)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_drift.wav" type="audio/wav"></audio>

Drift amount controls how unstable the oscillator is:

- **0.05** = studio-grade (Sequential, Oberheim)
- **0.15** = classic vintage (Minimoog, ARP) — the default
- **0.30** = barely-holding-it-together (old SH-101)

ADSR Envelopes
--------------

Here's a question: a piano and an organ can play the exact same note at
the exact same frequency. Why do they sound completely different? The
answer is the envelope -- the *shape* of the sound over time. A piano
hits hard and immediately starts fading. An organ snaps on at full
volume and stays there until you lift the key. A violin swells in
gradually. The frequency is the same; the envelope is what makes each
instrument feel like itself.

ADSR stands for Attack, Decay, Sustain, Release -- four stages that
describe how any sound's volume changes from the moment you press a key
to the moment it falls silent. Understanding ADSR is the single most
important thing you can learn about synthesis, because it's the
difference between a sound that feels like an instrument and a sound
that feels like a test tone.

Raw waveforms click at the start and end of each note. An ADSR envelope
shapes the amplitude over time for natural-sounding notes:

- **Attack** -- how quickly the sound reaches full volume.
- **Decay** -- how quickly it drops to the sustain level.
- **Sustain** -- the held volume while the note is on.
- **Release** -- how quickly it fades to silence after the note ends.

PyTheory includes 10 presets:

.. code-block:: python

   from pytheory import play, Envelope, Tone

   tone = Tone.from_string("C4", system="western")

   play(tone, envelope=Envelope.PIANO)     # Quick attack, natural decay
   play(tone, envelope=Envelope.PLUCK)     # Sharp attack, fast decay
   play(tone, envelope=Envelope.PAD)       # Slow fade in, lush sustain
   play(tone, envelope=Envelope.ORGAN)     # Instant on/off, no shaping
   play(tone, envelope=Envelope.BELL)      # Instant attack, long ring
   play(tone, envelope=Envelope.STRINGS)   # Gradual bow attack
   play(tone, envelope=Envelope.BOWED)     # Bow bite into sustain
   play(tone, envelope=Envelope.MALLET)    # Strike with ringing sustain
   play(tone, envelope=Envelope.STACCATO)  # Short and punchy
   play(tone, envelope=Envelope.NONE)      # Raw waveform, no shaping

Envelope Descriptions
~~~~~~~~~~~~~~~~~~~~~

===============  ================================================
Name             Character
===============  ================================================
``"piano"``      Quick attack, natural decay -- acoustic piano feel
``"pluck"``      Sharp attack, fast decay -- guitar pick, harp
``"pad"``        Slow fade in, lush sustain -- strings, synth pads
``"organ"``      Instant on/off -- Hammond organ, no shaping
``"bell"``       Instant attack, no sustain -- short metallic ring
``"strings"``    Gradual bow attack -- orchestral strings, slow
``"bowed"``      Bow bite into sustain -- solo strings, brass
``"mallet"``     Strike with ringing sustain -- vibraphone, celesta
``"staccato"``   Short and punchy -- funk stabs, percussive hits
``"none"``       Raw waveform, no amplitude shaping at all
===============  ================================================

Detune
------

Any synth can be fattened with the ``detune`` parameter — it renders
three oscillators per note: the center pitch plus one shifted up and
one shifted down by the specified number of cents. The slight frequency
differences create beating and width, like an analog synth with
oscillator drift.

.. code-block:: python

   # Juno-style analog drift — subtle, warm
   pad = score.part("pad", synth="saw", detune=15)

   # Trance supersaw territory — wide, shimmery
   lead = score.part("lead", synth="saw", detune=25)

   # Subtle thickening on a bass
   bass = score.part("bass", synth="pulse", detune=8)

   # Works on any synth — even FM
   bells = score.part("bells", synth="fm", detune=12)

Detune values:

- **5–10** = subtle thickening (barely noticeable, just warmer)
- **12–18** = classic analog drift (Juno, Prophet)
- **20–30** = wide and shimmery (trance, EDM)
- **40+** = extreme, almost chorus-like

This is different from the ``chorus`` effect — detune creates
additional oscillators at render time (three per note), while chorus
processes the audio after rendering with a modulated delay line.
Detune is "wider at the source," chorus is "wider after the fact."
Stack both for maximum fatness.

Stereo Placement
----------------

Every part can be placed in the stereo field with ``pan`` and ``spread``.

**Pan** positions a part left or right. Constant-power panning keeps
the perceived loudness even as you move across the field:

.. code-block:: python

   rhythm = score.part("rhythm", synth="saw", pan=-0.7)     # left
   lead = score.part("lead", synth="saw", pan=0.6)          # right
   bass = score.part("bass", synth="sine", pan=0.0)         # center
   hats = score.part("hats", synth="noise", pan=0.3)        # slightly right

Pan values: -1.0 (hard left), 0.0 (center), 1.0 (hard right).

**Spread** works with ``detune`` — the up-detuned oscillator goes to
the right channel and the down-detuned goes to the left, creating
stereo width at the source:

.. code-block:: python

   # Wide pad: detuned + spread across the stereo field
   pad = score.part(
       "pad",
       synth="saw",
       detune=20,
       spread=1.0,       # full L/R separation of detuned voices
       reverb=0.4,
   )

Spread values: 0.0 (detuned voices stay mono), 1.0 (full L/R split).
Stack with pan to offset the center of the spread.

Reverb is also stereo — the left and right channels get different
early reflection patterns, so the reverb tail occupies real space
in the stereo field rather than sitting dead center.

Physical Modeling
-----------------

Three synths go beyond traditional waveform synthesis into physical
modeling territory — they simulate how real instruments produce sound.

Karplus-Strong Pluck
~~~~~~~~~~~~~~~~~~~~

A burst of noise fed into a short delay line. The delay length sets
the pitch, the feedback filter models the string decaying. This is
how every physical modeling synth since 1983 does plucked strings.
It sounds genuinely like a real guitar, harp, or koto.

.. code-block:: python

   guitar = score.part("guitar", synth="pluck_synth")
   harp = score.part("harp", instrument="harp")  # uses pluck_synth

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_karplus.wav" type="audio/wav"></audio>

Hammond Organ
~~~~~~~~~~~~~

Additive synthesis with drawbar harmonics — sine waves at the
fundamental plus 2nd, 3rd, 4th, 5th, 6th, and 8th harmonics mixed
at musical levels. Warm, round, unmistakably organ.

.. code-block:: python

   organ = score.part("organ", synth="organ_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_organ.wav" type="audio/wav"></audio>

String Ensemble
~~~~~~~~~~~~~~~

Filtered sawtooth with body resonance formants at ~500 Hz and ~1500 Hz,
modeling the way a violin or cello body shapes the sound. Warmer and
more "wooden" than a raw saw wave.

.. code-block:: python

   violin = score.part("violin", synth="strings_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_strings.wav" type="audio/wav"></audio>

Dedicated Instrument Synths
--------------------------

Beyond the classic and physical modeling waveforms, PyTheory includes
36 dedicated instrument synths. Each one uses tailored synthesis
techniques -- additive harmonics, formant shaping, body resonance
modeling, and specialized envelopes -- to capture the character of a
specific acoustic instrument. These are the waveforms that bring the
total count to 56.

Piano Synth
~~~~~~~~~~~

Hammer-strike envelope with body resonance and subtle inharmonicity.
Models the way a felt hammer excites steel strings inside a wooden
soundboard.

.. code-block:: python

   piano = score.part("piano", synth="piano_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_piano.wav" type="audio/wav"></audio>

Rhodes Electric Piano
~~~~~~~~~~~~~~~~~~~~~

The Fender Rhodes — a rubber-tipped hammer strikes a steel tine
next to a tonebar, picked up by an electromagnetic pickup. Warm,
bell-like, with a bright metallic attack that mellows into a
singing sustain. The sound of jazz clubs, soul, and neo-soul.

.. code-block:: python

   rhodes = score.part("rhodes", synth="rhodes_synth")
   # Or use the instrument preset (adds tremolo + chorus)
   rhodes = score.part("rhodes", instrument="electric_piano")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_rhodes.wav" type="audio/wav"></audio>

Wurlitzer Electric Piano
~~~~~~~~~~~~~~~~~~~~~~~~

The Wurlitzer uses a vibrating steel reed (not a tine like Rhodes)
picked up by an electrostatic pickup. More nasal, reedy, and biting
— it barks and growls when played hard. Think Supertramp, Ray Charles.

.. code-block:: python

   wurli = score.part("wurli", synth="wurlitzer_synth")
   wurli = score.part("wurli", instrument="wurlitzer")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_wurlitzer.wav" type="audio/wav"></audio>

Mellotron
~~~~~~~~~

The original "sampler" — a 1960s keyboard where each key triggers a
strip of magnetic tape with a pre-recorded instrument. The mechanical
tape transport gives it a haunted, lo-fi quality that no digital
emulation fully captures: pitch wobbles from uneven capstan speed,
bandwidth limited to 300 Hz–6 kHz (like a worn cassette), soft tape
saturation, and tapes that physically run out after 8 seconds.

The Mellotron defined the sound of *Strawberry Fields Forever*,
*Stairway to Heaven*, and every prog rock record from 1969–1977.

Three tape banks are available via the ``tape`` parameter:

- ``"strings"`` (default) — the iconic MkII string section
- ``"flute"`` — breathy, haunting solo flute
- ``"choir"`` — ghostly vocal pad

**Use for:** prog rock, haunted textures, vintage orchestral color.

.. code-block:: python

   # Use instrument presets (includes reverb)
   strings = score.part("strings", instrument="mellotron_strings")
   flute = score.part("flute", instrument="mellotron_flute")
   choir = score.part("choir", instrument="mellotron_choir")

   # Or select the tape directly
   from pytheory import play, Synth, Tone
   play(Tone.from_string("C4"), synth=Synth.MELLOTRON, tape="flute", t=3000)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_mellotron.wav" type="audio/wav"></audio>

Vibraphone Synth
~~~~~~~~~~~~~~~~

Struck aluminum bars with motor-driven tremolo discs. The spinning
motor modulates the sound through the resonator tubes, creating the
signature vibraphone shimmer. Inharmonic bar modes at 1x, 2.76x, 5.4x.

.. code-block:: python

   vib = score.part("vib", synth="vibraphone_synth")
   vib = score.part("vib", instrument="vibraphone")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_vibraphone.wav" type="audio/wav"></audio>

Pipe Organ Synth
~~~~~~~~~~~~~~~~

Multiple ranks of pipes — principal 8', octave 4', fifteenth 2'.
Constant air pressure means no dynamics. Wind chiff at the attack.
Best with cathedral reverb.

.. code-block:: python

   organ = score.part("organ", synth="pipe_organ_synth")
   organ = score.part("organ", instrument="pipe_organ")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_pipe_organ.wav" type="audio/wav"></audio>

Choir Synth
~~~~~~~~~~~

Voices singing vowels shaped by formant bandpass filters. The glottal
source is filtered through vocal tract resonances — F1, F2, F3, F4 —
which is what makes "ah" sound different from "oo". Use ``lyric=``
to control the vowel. Best with ``ensemble=`` for a full section.

.. code-block:: python

   choir = score.part("choir", synth="choir_synth")
   choir = score.part("choir", instrument="choir")  # ensemble=6 + cathedral reverb
   choir.add("C4", Duration.WHOLE, lyric="ah")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_choir.wav" type="audio/wav"></audio>

Bass Guitar Synth
~~~~~~~~~~~~~~~~~

Plucked string model with finger-damped harmonics and low-end warmth.

.. code-block:: python

   bass = score.part("bass", synth="bass_guitar_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_bass_guitar.wav" type="audio/wav"></audio>

Flute Synth
~~~~~~~~~~~~

Breathy noise excitation through a resonant tube model, with
overblowing behavior at higher velocities.

.. code-block:: python

   flute = score.part("flute", synth="flute_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_flute.wav" type="audio/wav"></audio>

Trumpet Synth
~~~~~~~~~~~~~

Brass lip-buzz model with spectral brightness that increases with
velocity, plus a characteristic brassy edge from shaped harmonics.

.. code-block:: python

   trumpet = score.part("trumpet", synth="trumpet_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_trumpet.wav" type="audio/wav"></audio>

Clarinet Synth
~~~~~~~~~~~~~~

Cylindrical bore model producing mostly odd harmonics, giving the
characteristic hollow, woody tone.

.. code-block:: python

   clarinet = score.part("clarinet", synth="clarinet_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_clarinet.wav" type="audio/wav"></audio>

Oboe Synth
~~~~~~~~~~~

Double-reed model with nasal formant shaping and a buzzy, penetrating
timbre.

.. code-block:: python

   oboe = score.part("oboe", synth="oboe_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_oboe.wav" type="audio/wav"></audio>

Marimba Synth
~~~~~~~~~~~~~

Tuned bar model with a soft mallet attack and a warm, resonant decay
that emphasizes the fundamental.

.. code-block:: python

   marimba = score.part("marimba", synth="marimba_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_marimba.wav" type="audio/wav"></audio>

Harpsichord Synth
~~~~~~~~~~~~~~~~~

Plucked-string model with a bright, immediate attack and rapid decay
-- the characteristic "plink" of a quill plucking a string.

.. code-block:: python

   harpsi = score.part("harpsi", synth="harpsichord_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_harpsichord.wav" type="audio/wav"></audio>

Cello Synth
~~~~~~~~~~~

Bowed string model with body formants at cello resonance frequencies,
producing a rich, warm, sustained tone.

.. code-block:: python

   cello = score.part("cello", synth="cello_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_cello.wav" type="audio/wav"></audio>

Harp Synth
~~~~~~~~~~

Plucked string with longer sustain and gentle high-frequency rolloff,
modeling nylon strings on a resonant frame.

.. code-block:: python

   harp = score.part("harp", synth="harp_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_harp.wav" type="audio/wav"></audio>

Upright Bass Synth
~~~~~~~~~~~~~~~~~~

Pizzicato double bass with woody body resonance and a thumpy low end.

.. code-block:: python

   bass = score.part("bass", synth="upright_bass_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_upright_bass.wav" type="audio/wav"></audio>

Acoustic Guitar Synth
~~~~~~~~~~~~~~~~~~~~~

Steel-string model with pick transient, body resonance, and natural
string decay.

.. code-block:: python

   guitar = score.part("guitar", synth="acoustic_guitar_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_acoustic_guitar.wav" type="audio/wav"></audio>

Electric Guitar Synth
~~~~~~~~~~~~~~~~~~~~~

Magnetic pickup model with brighter harmonics and less body resonance
than the acoustic, ready for effects processing.

.. code-block:: python

   eguitar = score.part("eguitar", synth="electric_guitar_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_electric_guitar.wav" type="audio/wav"></audio>

Sitar Synth
~~~~~~~~~~~~

Sympathetic string resonance with the characteristic buzzy "jawari"
bridge, producing a shimmering, metallic sustain.

.. code-block:: python

   sitar = score.part("sitar", synth="sitar_synth")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_sitar.wav" type="audio/wav"></audio>

Timpani Synth
~~~~~~~~~~~~~

Large kettle drum with definite pitch. Inharmonic membrane modes
(1.0, 1.5, 1.99, 2.44), felt mallet attack, copper kettle resonance.
Use ``Part.roll()`` for crescendo timpani rolls.

.. code-block:: python

   timp = score.part("timp", synth="timpani_synth")
   timp.roll("C3", Duration.WHOLE, velocity_start=20, velocity_end=110)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_timpani.wav" type="audio/wav"></audio>

Saxophone Synth
~~~~~~~~~~~~~~~

Single reed through a conical brass bore. All harmonics with strong
mids, reed buzz, and brass body warmth. Four presets: ``saxophone``,
``alto_sax``, ``tenor_sax``, ``bari_sax``.

.. code-block:: python

   sax = score.part("sax", instrument="tenor_sax")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_saxophone.wav" type="audio/wav"></audio>

Pedal Steel Synth
~~~~~~~~~~~~~~~~~

The Nashville crying sound — singing harmonics with slow vibrato
and long sustain. Pairs naturally with spring reverb.

.. code-block:: python

   steel = score.part("steel", instrument="pedal_steel")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_pedal_steel.wav" type="audio/wav"></audio>

Theremin Synth
~~~~~~~~~~~~~~

Pure sine with natural hand wobble — the eerie sci-fi sound.
Best used with legato and glide for continuous pitch.

.. code-block:: python

   theremin = score.part("theremin", instrument="theremin")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_theremin.wav" type="audio/wav"></audio>

Kalimba Synth
~~~~~~~~~~~~~

Metal tines on a wooden body. Bright, bell-like attack with
inharmonic overtones (modes at 1x, 2.92x, 5.4x).

.. code-block:: python

   kalimba = score.part("kalimba", instrument="kalimba")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_kalimba.wav" type="audio/wav"></audio>

Steel Drum Synth
~~~~~~~~~~~~~~~~

Hammered metal pan with bright, ringing, tropical character.
Inharmonic partials at 2.0x, 3.01x, 4.1x, 5.3x.

.. code-block:: python

   pan = score.part("pan", instrument="steel_drum")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_steel_drum.wav" type="audio/wav"></audio>

Accordion Synth
~~~~~~~~~~~~~~~

Musette-tuned doubled reeds — two slightly detuned reed sets
create natural beating. Bellows pressure swell modulates amplitude.

.. code-block:: python

   acc = score.part("acc", instrument="accordion")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_accordion.wav" type="audio/wav"></audio>

Didgeridoo Synth
~~~~~~~~~~~~~~~~

Deep cylindrical drone with shifting formant overtones. The
overtone singing effect sweeps a resonant peak between 500-1500Hz.
Best with cave reverb.

.. code-block:: python

   didg = score.part("didg", instrument="didgeridoo")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_didgeridoo.wav" type="audio/wav"></audio>

Bagpipe Synth
~~~~~~~~~~~~~

Bright chanter reed with constant bag pressure. All harmonics
peaked around 3-7 (the piercing brightness). No dynamics — always ff.

.. code-block:: python

   pipes = score.part("pipes", instrument="bagpipe")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_bagpipe.wav" type="audio/wav"></audio>

Banjo Synth
~~~~~~~~~~~

Steel strings on a drum-head membrane body. The membrane gives
nasal, ringy resonance with faster decay than guitar.

.. code-block:: python

   banjo = score.part("banjo", instrument="banjo")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_banjo.wav" type="audio/wav"></audio>

Mandolin Synth
~~~~~~~~~~~~~~

Paired steel strings in 4 courses — natural chorus from the
doubled unison strings. Bright, ringing, fast attack.

.. code-block:: python

   mando = score.part("mando", instrument="mandolin")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_mandolin.wav" type="audio/wav"></audio>

Ukulele Synth
~~~~~~~~~~~~~

Nylon strings on a small body. Mid-heavy resonance (no deep bass),
softer attack than guitar, shorter sustain.

.. code-block:: python

   uke = score.part("uke", instrument="ukulele")

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_ukulele.wav" type="audio/wav"></audio>

Granular Synth
~~~~~~~~~~~~~~

Grain cloud synthesis — chops a source waveform into tiny overlapping
grains (10-200ms), each windowed and optionally pitch/time scattered.
Creates textures impossible with other synthesis: frozen tones,
shimmering clouds, evolving pads, glitchy stutters.

.. code-block:: python

   # Atmospheric granular pad
   pad = score.part("pad", instrument="granular_pad")

   # Granular with filter envelope sweep + resonance
   texture = score.part("texture", synth="granular_synth", envelope="pad",
                        filter_amount=4000, filter_attack=0.5,
                        filter_decay=1.5, filter_sustain=0.3,
                        lowpass=600, lowpass_q=3.0,
                        reverb=0.5, reverb_type="taj_mahal")

Parameters (passed as synth kwargs):

- ``grain_size``: Duration per grain in seconds (default 0.04).
- ``density``: Grains per second (default 50). Higher = denser cloud.
- ``scatter``: Random position jitter 0-1 (default 0.5).
- ``pitch_var``: Per-grain pitch randomization in cents (default 12).
- ``source``: Base waveform — ``"saw"``, ``"sine"``, ``"triangle"``,
  ``"square"``, ``"noise"``.

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_granular.wav" type="audio/wav"></audio>

Crotales
~~~~~~~~

Small tuned bronze discs (antique cymbals) struck with brass mallets.
Bright, crystalline, bell-like tone with strong upper harmonics that
rings for a long time. Nearly harmonic partials give crotales their
penetrating brilliance — they cut through any orchestra.

.. code-block:: python

   crotales = score.part("crotales", synth="crotales_synth", envelope="none",
                         reverb=0.3)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_crotales.wav" type="audio/wav"></audio>

Tingsha
~~~~~~~

Two small Tibetan cymbals joined by a cord, clashed together. Both discs
ring at slightly different frequencies, producing a bright ping with
pronounced beating — the wavering interference between the two is the
whole character of the sound.

.. code-block:: python

   tingsha = score.part("tingsha", synth="tingsha_synth", envelope="none",
                        reverb=0.4)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_tingsha.wav" type="audio/wav"></audio>

Singing Bowl (Strike)
~~~~~~~~~~~~~~~~~~~~~

Tibetan/Himalayan singing bowl struck with a mallet. The impact excites
inharmonic partials that ring and slowly beat against each other as
near-degenerate mode pairs interfere. Higher modes fade quickly, leaving
the fundamental shimmering for seconds.

.. code-block:: python

   bowl = score.part("bowl", synth="singing_bowl_strike_synth", envelope="none",
                     reverb=0.4)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_singing_bowl_strike.wav" type="audio/wav"></audio>

Singing Bowl (Ring)
~~~~~~~~~~~~~~~~~~~

Rim-rubbed singing bowl — the mallet traces the rim, slowly building the
fundamental into a sustained, pulsing tone. Upper harmonics shimmer in
and out as the bowl resonates.

.. code-block:: python

   bowl = score.part("bowl", synth="singing_bowl_ring_synth", envelope="none",
                     reverb=0.4)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/synth_singing_bowl_ring.wav" type="audio/wav"></audio>

Rain Stick
~~~~~~~~~~

Cascading pebbles through a cactus tube with internal pins. Two variants:
steep angle (fast cascade) and shallow angle (slow trickle).

.. code-block:: python

   p.hit(DrumSound.RAINSTICK, Duration.WHOLE * 3)       # steep — fast cascade
   p.hit(DrumSound.RAINSTICK_SLOW, Duration.WHOLE * 4)  # shallow — gentle trickle

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/rainstick.wav" type="audio/wav"></audio>
   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/rainstick_slow.wav" type="audio/wav"></audio>

Ocean Drum
~~~~~~~~~~

Steel beads rolling inside a frame drum — tilting produces a smooth surf wash.

.. code-block:: python

   p.hit(DrumSound.OCEAN_DRUM, Duration.WHOLE * 3)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/ocean_drum.wav" type="audio/wav"></audio>

Cabasa
~~~~~~

Metal bead chain scraped against a textured cylinder — brighter and
more metallic than a shaker.

.. code-block:: python

   p.hit(DrumSound.CABASA, Duration.EIGHTH)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/cabasa.wav" type="audio/wav"></audio>

Wind Chimes
~~~~~~~~~~~

Suspended metal tubes struck by hand or breeze. Each tube rings at
its own pitch with slight time offsets.

.. code-block:: python

   p.hit(DrumSound.WIND_CHIMES, Duration.WHOLE * 3)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/wind_chimes.wav" type="audio/wav"></audio>

Finger Cymbal
~~~~~~~~~~~~~

Single small cymbal tap (zill) — bright metallic ping.

.. code-block:: python

   p.hit(DrumSound.FINGER_CYMBAL, Duration.HALF)

.. raw:: html

   <audio controls style="width:100%;margin:0.3em 0 0.5em"><source src="../_static/audio/finger_cymbal.wav" type="audio/wav"></audio>

Analog Oscillator Drift
~~~~~~~~~~~~~~~~~~~~~~~~

All waveform synths support the ``analog_drift`` parameter, which adds
subtle, slow random pitch variation to each oscillator -- modeling the
voltage instability of vintage analog circuits. This is what makes a
real Minimoog sound slightly different on every note, and why analog
synths feel "alive" compared to their digital counterparts.

.. code-block:: python

   # Subtle vintage drift
   pad = score.part("pad", synth="saw", analog_drift=0.1)

   # More pronounced, wobbly analog character
   lead = score.part("lead", synth="square", analog_drift=0.3)

Drift values:

- **0.05--0.1** = subtle warmth (studio-grade analog)
- **0.15--0.25** = noticeable drift (vintage gear warming up)
- **0.3+** = unstable, wobbly (broken tape machine)

Instrument Presets
------------------

Instead of choosing synth + envelope + effects manually, use an
instrument preset — 60+ predefined combinations that approximate real
instruments:

.. code-block:: python

   piano = score.part("piano", instrument="piano")
   violin = score.part("violin", instrument="violin")
   guitar = score.part("guitar", instrument="acoustic_guitar")
   organ = score.part("organ", instrument="organ")
   bass = score.part("bass", instrument="upright_bass")

Available instruments:

**Keys**: piano, electric_piano, organ, harpsichord, celesta, music_box,
accordion

**Strings**: violin, viola, cello, contrabass, string_ensemble

**Woodwinds**: flute, clarinet, oboe, bassoon, saxophone, alto_sax,
tenor_sax, bari_sax

**Brass**: trumpet, trombone, french_horn, tuba, brass_ensemble

**Plucked**: acoustic_guitar, electric_guitar, clean_guitar, crunch_guitar,
distorted_guitar, orange_crunch, metal_guitar, bass_guitar, upright_bass,
harp, sitar, koto, banjo, mandolin, mandola, ukulele

**World/Exotic**: pedal_steel, theremin, kalimba, steel_drum, didgeridoo,
bagpipe, singing_bowl, singing_bowl_ring, tingsha

**Synth**: synth_lead, synth_pad, synth_bass, acid_bass, 808_bass,
granular_pad, granular_texture, vocal, choir

**Mellotron**: mellotron, mellotron_strings, mellotron_flute, mellotron_choir

**Analog**: sync_lead, sync_lead_bright, ring_mod_bell, ring_mod_metallic,
wavefold_warm, wavefold_gnarly, drift_saw, drift_square, analog_pad,
analog_bass

**Percussion**: vibraphone, marimba, xylophone, glockenspiel, tubular_bells,
timpani, crotales

Explicit kwargs override preset defaults:

.. code-block:: python

   # Piano with extra reverb
   piano = score.part("piano", instrument="piano", reverb=0.5)

   # Violin panned left
   violin = score.part("v", instrument="violin", pan=-0.4)

Choosing Synth and Envelope Combos
----------------------------------

The right combination of synth and envelope defines the character of a
voice. This is where you stop thinking about waveforms and start
thinking about *instruments*. Here are some starting points:

- **Funk stabs:** ``saw`` + ``staccato`` -- bright, punchy, rhythmic.
- **Jazz keys:** ``fm`` + ``bell`` -- glassy DX7 electric piano.
- **Ambient pads:** ``supersaw`` + ``pad`` -- massive, slow-building wash.
- **Acid bass:** ``saw`` + ``pluck`` with lowpass and glide -- 303-style.
- **Chiptune lead:** ``square`` + ``none`` -- raw 8-bit.
- **Film strings:** ``triangle`` + ``strings`` -- soft, bowed, organic.
- **Sub bass:** ``sine`` + ``pluck`` with lowpass -- deep and round.
- **Retro synth:** ``pwm_slow`` + ``pad`` -- Juno-style analog warmth.
- **Percussive hit:** ``noise`` + ``staccato`` with lowpass -- snare layer.
- **E-piano ballad:** ``fm`` + ``piano`` with reverb -- intimate jazz club.

Some practical combos worth memorizing:

- ``saw`` + ``staccato`` + legato = **acid 303 line.** Add a resonant
  lowpass and some glide and you're in a warehouse in 1988.
- ``fm`` + ``bell`` = **jazz vibraphone.** The glassy, harmonic-rich
  attack with a long ring-out. Add reverb for a late-night club feel.
- ``supersaw`` + ``pad`` = **ambient wash.** The slow attack lets the
  detuned oscillators build into a shimmering wall. Add chorus and
  long reverb and you're scoring a nature documentary.
- ``saw`` + ``pluck`` = **funk stab.** Short, sharp, bright. The
  sound of Nile Rodgers' right hand.
- ``hard_sync`` + ``pluck`` = **prophet lead.** Bright formant peak
  that cuts through any mix. The opening riff of every 80s synth solo.
- ``wavefold`` + ``organ`` = **west coast bass.** Warm, harmonically
  rich sine-derivative that pairs beautifully with a lowpass after.
- ``drift`` + ``pad`` = **analog pad.** A sawtooth that breathes and
  wobbles like a real VCO. Add chorus and reverb for Juno vibes.
- ``mellotron_synth`` + ``organ`` = **prog strings.** Haunted tape
  machine. Add cathedral reverb and you're in 1972.
