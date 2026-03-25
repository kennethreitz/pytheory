Synthesizers
============

PyTheory includes 10 built-in waveforms and 8 ADSR envelope presets.
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

PyTheory includes 8 presets:

.. code-block:: python

   from pytheory import play, Envelope, Tone

   tone = Tone.from_string("C4", system="western")

   play(tone, envelope=Envelope.PIANO)     # Quick attack, natural decay
   play(tone, envelope=Envelope.PLUCK)     # Sharp attack, fast decay
   play(tone, envelope=Envelope.PAD)       # Slow fade in, lush sustain
   play(tone, envelope=Envelope.ORGAN)     # Instant on/off, no shaping
   play(tone, envelope=Envelope.BELL)      # Instant attack, long ring
   play(tone, envelope=Envelope.STRINGS)   # Gradual bow attack
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
``"bell"``       Instant attack, long ring -- vibraphone, tubular
``"strings"``    Gradual bow attack -- orchestral strings, slow
``"staccato"``   Short and punchy -- funk stabs, percussive hits
``"none"``       Raw waveform, no amplitude shaping at all
===============  ================================================

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
