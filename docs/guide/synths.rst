Synthesizers
============

PyTheory includes 27 built-in waveforms and 10 ADSR envelope presets.
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

Sawtooth
~~~~~~~~

Contains all harmonics (both odd and even), each at amplitude 1/n.
The richest of the classic waveforms — bright, buzzy, and aggressive.
Named for its ramp shape.

**Use for:** leads, brass, pads, anything that needs presence and bite.

.. code-block:: python

   play(tone, synth=Synth.SAW)

Triangle
~~~~~~~~

Contains only odd harmonics, each at amplitude 1/n-squared. Softer and
more mellow than sawtooth — somewhere between sine and saw. Often
described as "woody" or "hollow."

**Use for:** flute-like leads, mellow bass, gentle pads.

.. code-block:: python

   play(tone, synth=Synth.TRIANGLE)

Square
~~~~~~

Contains only odd harmonics, each at amplitude 1/n. Sounds hollow and
punchy — the classic chiptune / 8-bit sound. A special case of the
pulse wave with a 50% duty cycle.

**Use for:** chiptune, 8-bit game music, hollow leads, sub-octave bass.

.. code-block:: python

   play(tone, synth=Synth.SQUARE)

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

FM Synthesis
~~~~~~~~~~~~

Frequency modulation -- one oscillator (the modulator) modulates the
frequency of another (the carrier), producing complex inharmonic
spectra. This is how the Yamaha DX7 works -- the best-selling
synthesizer of all time. Released in 1983, it was suddenly everywhere:
the electric piano in every Whitney Houston ballad, the bass in every
Depeche Mode track, the bells in a thousand TV jingles. If you heard
pop music in the 80s, you heard FM synthesis.

**Use for:** electric piano (rhodes), bells, metallic leads, jazz chords.

.. code-block:: python

   rhodes = score.part(
       "rhodes",
       synth="fm",
       envelope="piano",
       volume=0.3,
       reverb=0.4,
   )

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

PWM Fast
~~~~~~~~

Pulse width modulation with a fast LFO. The rapid duty cycle sweep
produces a natural chorus/vibrato effect built into the waveform itself.

**Use for:** animated leads, vibrato textures, movement without effects.

.. code-block:: python

   lead = score.part("lead", synth="pwm_fast", envelope="pluck", volume=0.5)

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

Hammond Organ
~~~~~~~~~~~~~

Additive synthesis with drawbar harmonics — sine waves at the
fundamental plus 2nd, 3rd, 4th, 5th, 6th, and 8th harmonics mixed
at musical levels. Warm, round, unmistakably organ.

.. code-block:: python

   organ = score.part("organ", synth="organ_synth")

String Ensemble
~~~~~~~~~~~~~~~

Filtered sawtooth with body resonance formants at ~500 Hz and ~1500 Hz,
modeling the way a violin or cello body shapes the sound. Warmer and
more "wooden" than a raw saw wave.

.. code-block:: python

   violin = score.part("violin", synth="strings_synth")

Dedicated Instrument Synths
--------------------------

Beyond the classic and physical modeling waveforms, PyTheory includes
14 dedicated instrument synths. Each one uses tailored synthesis
techniques -- additive harmonics, formant shaping, body resonance
modeling, and specialized envelopes -- to capture the character of a
specific acoustic instrument. These are the waveforms that bring the
total count to 27.

Piano Synth
~~~~~~~~~~~

Hammer-strike envelope with body resonance and subtle inharmonicity.
Models the way a felt hammer excites steel strings inside a wooden
soundboard.

.. code-block:: python

   piano = score.part("piano", synth="piano_synth")

Bass Guitar Synth
~~~~~~~~~~~~~~~~~

Plucked string model with finger-damped harmonics and low-end warmth.

.. code-block:: python

   bass = score.part("bass", synth="bass_guitar_synth")

Flute Synth
~~~~~~~~~~~~

Breathy noise excitation through a resonant tube model, with
overblowing behavior at higher velocities.

.. code-block:: python

   flute = score.part("flute", synth="flute_synth")

Trumpet Synth
~~~~~~~~~~~~~

Brass lip-buzz model with spectral brightness that increases with
velocity, plus a characteristic brassy edge from shaped harmonics.

.. code-block:: python

   trumpet = score.part("trumpet", synth="trumpet_synth")

Clarinet Synth
~~~~~~~~~~~~~~

Cylindrical bore model producing mostly odd harmonics, giving the
characteristic hollow, woody tone.

.. code-block:: python

   clarinet = score.part("clarinet", synth="clarinet_synth")

Oboe Synth
~~~~~~~~~~~

Double-reed model with nasal formant shaping and a buzzy, penetrating
timbre.

.. code-block:: python

   oboe = score.part("oboe", synth="oboe_synth")

Marimba Synth
~~~~~~~~~~~~~

Tuned bar model with a soft mallet attack and a warm, resonant decay
that emphasizes the fundamental.

.. code-block:: python

   marimba = score.part("marimba", synth="marimba_synth")

Harpsichord Synth
~~~~~~~~~~~~~~~~~

Plucked-string model with a bright, immediate attack and rapid decay
-- the characteristic "plink" of a quill plucking a string.

.. code-block:: python

   harpsi = score.part("harpsi", synth="harpsichord_synth")

Cello Synth
~~~~~~~~~~~

Bowed string model with body formants at cello resonance frequencies,
producing a rich, warm, sustained tone.

.. code-block:: python

   cello = score.part("cello", synth="cello_synth")

Harp Synth
~~~~~~~~~~

Plucked string with longer sustain and gentle high-frequency rolloff,
modeling nylon strings on a resonant frame.

.. code-block:: python

   harp = score.part("harp", synth="harp_synth")

Upright Bass Synth
~~~~~~~~~~~~~~~~~~

Pizzicato double bass with woody body resonance and a thumpy low end.

.. code-block:: python

   bass = score.part("bass", synth="upright_bass_synth")

Acoustic Guitar Synth
~~~~~~~~~~~~~~~~~~~~~

Steel-string model with pick transient, body resonance, and natural
string decay.

.. code-block:: python

   guitar = score.part("guitar", synth="acoustic_guitar_synth")

Electric Guitar Synth
~~~~~~~~~~~~~~~~~~~~~

Magnetic pickup model with brighter harmonics and less body resonance
than the acoustic, ready for effects processing.

.. code-block:: python

   eguitar = score.part("eguitar", synth="electric_guitar_synth")

Sitar Synth
~~~~~~~~~~~~

Sympathetic string resonance with the characteristic buzzy "jawari"
bridge, producing a shimmering, metallic sustain.

.. code-block:: python

   sitar = score.part("sitar", synth="sitar_synth")

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
instrument preset — 40+ predefined combinations that approximate real
instruments:

.. code-block:: python

   piano = score.part("piano", instrument="piano")
   violin = score.part("violin", instrument="violin")
   guitar = score.part("guitar", instrument="acoustic_guitar")
   organ = score.part("organ", instrument="organ")
   bass = score.part("bass", instrument="upright_bass")

Available instruments:

**Keys**: piano, electric_piano, organ, harpsichord, celesta, music_box

**Strings**: violin, viola, cello, contrabass, string_ensemble

**Woodwinds**: flute, clarinet, oboe, bassoon

**Brass**: trumpet, trombone, french_horn, tuba, brass_ensemble

**Plucked**: acoustic_guitar, electric_guitar, distorted_guitar,
bass_guitar, upright_bass, harp, sitar, koto

**Synth**: synth_lead, synth_pad, synth_bass, acid_bass, 808_bass

**Percussion**: vibraphone, marimba, xylophone, glockenspiel, tubular_bells

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
