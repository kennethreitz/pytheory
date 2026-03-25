Effects
=======

Each part in a Score can have its own effects chain. Effects are set at
part creation and applied per-part before mixing, so every voice gets
independent processing.

Signal Chain
------------

Effects are applied in this fixed order::

    Signal --> Distortion --> Chorus --> Lowpass Filter --> Delay --> Reverb --> Mix

- **Distortion** first: drives the raw signal before filtering (like
  plugging a guitar into a fuzz pedal before the amp).
- **Chorus** second: thickens the distorted signal.
- **Lowpass** third: shapes the tone (like a tone knob on an amp).
- **Delay** fourth: echoes the shaped signal (tap delay / tape echo).
- **Reverb** last: places everything in a space (room / hall).

Distortion
----------

Soft-clip waveshaping using ``tanh`` — models the warm saturation of an
overdriven tube amplifier. At low drive levels it adds harmonic warmth;
at high levels it becomes an aggressive fuzz.

Parameters:

- ``distortion``: Wet/dry mix, 0.0--1.0.
- ``distortion_drive``: Gain before clipping (default 3.0).

  - 0.5--2 = subtle warmth (tube preamp)
  - 3--8 = overdrive (cranked amp)
  - 10+ = fuzz

.. code-block:: pycon

   >>> # Warm tube saturation on a bass
   >>> bass = score.part("bass", synth="sine", envelope="pluck",
   ...                   distortion=0.3, distortion_drive=2.0)

   >>> # Heavy fuzz on a lead
   >>> lead = score.part("lead", synth="saw", envelope="staccato",
   ...                   distortion=0.8, distortion_drive=10.0)

Chorus
------

A slightly detuned, LFO-modulated delayed copy mixed back in. Thickens
the sound like two musicians playing the same part — the signature
effect of the Roland Juno synthesizers.

Parameters:

- ``chorus``: Wet/dry mix, 0.0--1.0.
- ``chorus_rate``: LFO speed in Hz. 0.5--1 = slow shimmer, 2--4 = vibrato.
- ``chorus_depth``: Modulation depth in seconds (default 0.003).

.. code-block:: pycon

   >>> # Juno-style pad chorus
   >>> pad = score.part("pad", synth="supersaw", envelope="pad",
   ...                  chorus=0.5, chorus_rate=1.5, chorus_depth=0.003)

   >>> # Subtle thickening on a clean lead
   >>> lead = score.part("lead", synth="triangle", envelope="pluck",
   ...                   chorus=0.2, chorus_rate=0.8)

Lowpass Filter
--------------

A 12 dB/octave biquad lowpass filter with resonance — the sound of
analog synthesizers. Removes frequencies above the cutoff; the resonance
(Q) parameter adds a peak at the cutoff frequency for that classic
"acid squelch."

Parameters:

- ``lowpass``: Cutoff frequency in Hz (0 = off). Reference points:

  - 200--400 Hz = deep sub bass
  - 800--1500 Hz = warm / muffled
  - 2000--4000 Hz = present lead
  - 5000+ Hz = subtle rolloff

- ``lowpass_q``: Resonance / Q factor (default 0.707 = Butterworth flat).

  - 1.0 = slight peak
  - 2.0 = pronounced
  - 5.0+ = aggressive acid squelch

.. code-block:: pycon

   >>> # Round bass with gentle filtering
   >>> bass = score.part("bass", synth="sine", envelope="pluck",
   ...                   lowpass=400, lowpass_q=1.5)

   >>> # Acid squelch on a saw lead
   >>> acid = score.part("acid", synth="saw", envelope="staccato",
   ...                   lowpass=1500, lowpass_q=5.0, legato=True, glide=0.03)

Delay
-----

Tempo-synced echoes with feedback. Each repeat feeds back into the
delay line, creating rhythmic echo trails. High feedback values produce
the cascading, self-oscillating echoes of dub reggae.

Parameters:

- ``delay``: Wet/dry mix, 0.0--1.0.
- ``delay_time``: Time between echoes in seconds. Musically useful
  values at 120 bpm: 0.25 (8th note), 0.375 (dotted 8th),
  0.5 (quarter note).
- ``delay_feedback``: How much each echo feeds back (0.0--1.0).

  - 0.3 = a few repeats
  - 0.5 = many repeats
  - 0.7+ = runaway (dub style)

.. code-block:: pycon

   >>> # Dotted-eighth slapback on a lead
   >>> lead = score.part("lead", synth="triangle", envelope="strings",
   ...                   delay=0.3, delay_time=0.375, delay_feedback=0.4)

   >>> # Dub-style runaway echoes
   >>> melodica = score.part("melodica", synth="triangle", envelope="pluck",
   ...                       delay=0.5, delay_time=0.66, delay_feedback=0.55)

Reverb
------

A Schroeder reverb using 4 parallel comb filters and 2 series allpass
filters. Simulates the natural reflections of a room, hall, or
cathedral.

Parameters:

- ``reverb``: Wet/dry mix, 0.0--1.0.

  - 0.2--0.4 = subtle space
  - 0.5--0.8 = ambient / dub

- ``reverb_decay``: Tail length in seconds.

  - 0.5 = small room
  - 1.5 = hall
  - 3.0+ = cathedral / dub

.. code-block:: pycon

   >>> # Jazz club ambience
   >>> rhodes = score.part("rhodes", synth="fm", envelope="piano",
   ...                     reverb=0.4, reverb_decay=1.8)

   >>> # Cathedral wash for ambient pads
   >>> pad = score.part("pad", synth="supersaw", envelope="pad",
   ...                  reverb=0.7, reverb_decay=4.0)

Combining Effects
-----------------

Effects stack naturally. Here are some real-world combinations:

Dub
~~~

Distortion warmth into filtered delay into deep reverb:

.. code-block:: pycon

   >>> melodica = score.part("melodica", synth="triangle", envelope="pluck",
   ...                       distortion=0.2, distortion_drive=2.0,
   ...                       lowpass=2000, lowpass_q=1.2,
   ...                       delay=0.5, delay_time=0.66, delay_feedback=0.55,
   ...                       reverb=0.4, reverb_decay=2.5)

Acid
~~~~

Resonant lowpass with distortion and delay:

.. code-block:: pycon

   >>> acid = score.part("acid", synth="saw", envelope="staccato",
   ...                   lowpass=1500, lowpass_q=3.0,
   ...                   distortion=0.4, distortion_drive=4.0,
   ...                   delay=0.3, delay_time=0.242, delay_feedback=0.4)

Ambient
~~~~~~~

Wide chorus, long reverb, gentle delay:

.. code-block:: pycon

   >>> ambient = score.part("ambient", synth="supersaw", envelope="pad",
   ...                      chorus=0.4, chorus_rate=0.5,
   ...                      delay=0.3, delay_time=0.5, delay_feedback=0.5,
   ...                      reverb=0.7, reverb_decay=4.0)

808 Bass
~~~~~~~~

Subtle saturation and deep filtering for hip-hop sub bass:

.. code-block:: pycon

   >>> bass = score.part("bass", synth="sine", envelope="pluck",
   ...                   lowpass=200, lowpass_q=1.8,
   ...                   distortion=0.4, distortion_drive=2.0)

Automation
----------

``Part.set()`` changes effect parameters mid-song at the current beat
position. The renderer splits the audio at automation points and
processes each section independently:

.. code-block:: pycon

   >>> lead = score.part("lead", synth="saw", lowpass=400, lowpass_q=3.0)

   >>> # Verse: filtered and clean
   >>> lead.arpeggio("Cm", bars=4, pattern="up", octaves=2)

   >>> # Chorus: filter opens, chorus kicks in
   >>> lead.set(lowpass=2000, chorus=0.3)
   >>> lead.arpeggio("Fm", bars=4, pattern="updown", octaves=2)

   >>> # Drop: full send
   >>> lead.set(lowpass=4000, distortion=0.7, reverb=0.3)
   >>> lead.arpeggio("Gm", bars=4, pattern="updown", octaves=2)

Any parameter can be automated: ``lowpass``, ``lowpass_q``, ``reverb``,
``reverb_decay``, ``delay``, ``delay_time``, ``delay_feedback``,
``distortion``, ``distortion_drive``, ``chorus``, ``volume``.

LFO Automation
--------------

``Part.lfo()`` automates a parameter with a low-frequency oscillator,
generating smooth sweeps over time. This is how filter sweeps, tremolo,
and auto-wah effects work.

.. code-block:: pycon

   >>> lead = score.part("lead", synth="saw", lowpass=400)

   >>> # Slow filter sweep: 400 -> 3000 Hz over 8 bars
   >>> lead.lfo("lowpass", rate=0.125, min=400, max=3000, bars=8)
   >>> lead.arpeggio("Cm", bars=8, pattern="up", octaves=2)

Parameters:

- ``param``: Parameter name to modulate (``"lowpass"``, ``"reverb"``,
  ``"distortion"``, ``"volume"``, ``"chorus"``, ``"delay"``).
- ``rate``: LFO speed in cycles per bar (default 0.5 = one sweep
  every 2 bars). 0.25 = very slow, 1 = once per bar, 4 = four times
  per bar.
- ``min`` / ``max``: Parameter value range.
- ``bars``: Number of bars to run the LFO over (default 4).
- ``shape``: Waveform shape.

  - ``"sine"`` -- smooth, natural sweep
  - ``"triangle"`` -- linear up/down
  - ``"saw"`` -- ramp up, snap back
  - ``"square"`` -- abrupt on/off

- ``resolution``: How often to insert automation points, in beats
  (default 0.25 = every 16th note). Lower values = smoother curves.

Stacking Multiple LFOs
~~~~~~~~~~~~~~~~~~~~~~~

Call ``.lfo()`` multiple times to modulate different parameters
simultaneously:

.. code-block:: pycon

   >>> lead = score.part("lead", synth="saw", lowpass=800, reverb=0.1)

   >>> # Filter opens over 8 bars
   >>> lead.lfo("lowpass", rate=0.125, min=400, max=4000, bars=8)
   >>> # Reverb swells in and out every 2 bars
   >>> lead.lfo("reverb", rate=0.5, min=0.1, max=0.6, bars=8, shape="triangle")
   >>> # Volume tremolo
   >>> lead.lfo("volume", rate=2, min=0.3, max=0.6, bars=8, shape="sine")

   >>> lead.arpeggio("Cm", bars=8, pattern="updown", octaves=2)
