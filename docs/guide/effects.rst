Effects
=======

Effects are how recorded music gets its character. A guitar without
reverb sounds like it's being played in a closet. A vocal without
compression sounds thin and amateur. A synth without filtering sounds
like a test signal. Effects are the difference between "notes" and
"music" -- they put the sound in a space, give it texture, and make it
feel alive.

Every record you've ever loved was shaped by effects. The cavernous
reverb on a Phil Collins drum hit. The tape delay on a reggae vocal.
The distortion on a Hendrix guitar. The chorus on an 80s synth pad.
These aren't decorations added after the fact; they're fundamental to
the sound itself.

Each part in a Score can have its own effects chain. Effects are set at
part creation and applied per-part before mixing, so every voice gets
independent processing.

Signal Chain
------------

The order of effects matters -- a lot. Distortion before a lowpass
filter means you're generating all those rich, crunchy harmonics and
then sculpting them with the filter. That's warm, controllable,
musical. Filter before distortion means you're distorting the already-
filtered signal -- a different, often harsher character. The fixed
order in PyTheory matches classic analog synth architecture, the same
signal path used by the Moog, the TB-303, and most hardware synths.
It's a well-tested order that sounds good by default.

Effects are applied in this fixed order::

    Signal --> Saturation --> Tremolo --> Distortion --> Cabinet --> Chorus
          --> Phaser --> Highpass --> Lowpass --> Delay --> Reverb --> Mix

Additionally, these per-note effects are applied before the part effects chain:

- **Sub-oscillator**: octave-below sine mixed in at the oscillator stage
- **Noise layer**: filtered noise mixed per-note for breath/transients
- **Filter envelope**: per-note lowpass sweep (attack/decay/sustain)
- **Velocity → brightness**: harder velocity = brighter filter cutoff

Part-level effects:

- **Saturation** first: subtle even-harmonic warmth (tape/tube color).
- **Tremolo** second: amplitude LFO modulation.
- **Distortion** third: drives the signal before filtering.
- **Cabinet** fourth: speaker cab simulation (rolloff + presence bump).
- **Chorus** fifth: thickens the signal.
- **Phaser** sixth: swept allpass notches.
- **Highpass** seventh: removes low-frequency mud.
- **Lowpass** eighth: shapes the tone (like a tone knob on an amp).
- **Delay** ninth: echoes the shaped signal (tap delay / tape echo).
- **Reverb** last: places everything in a space (room / hall).

Distortion
----------

You know what distortion sounds like -- it's the sound of rock and roll.
An electric guitar through a cranked amplifier. But at lower levels,
distortion is subtler: it adds warmth, presence, and harmonic richness.
This is why producers run clean signals through tape machines and tube
preamps. A little saturation makes everything sound more "real."

Soft-clip waveshaping using ``tanh`` -- models the warm saturation of an
overdriven tube amplifier. At low drive levels it adds harmonic warmth;
at high levels it becomes an aggressive fuzz.

Parameters:

- ``distortion``: Wet/dry mix, 0.0--1.0.
- ``distortion_drive``: Gain before clipping (default 3.0).

  - 0.5--2 = subtle warmth (tube preamp)
  - 3--8 = overdrive (cranked amp)
  - 10+ = fuzz

.. code-block:: python

   # Warm tube saturation on a bass
   bass = score.part(
       "bass",
       synth="sine",
       envelope="pluck",
       distortion=0.3,
       distortion_drive=2.0,
   )

   # Heavy fuzz on a lead
   lead = score.part(
       "lead",
       synth="saw",
       envelope="staccato",
       distortion=0.8,
       distortion_drive=10.0,
   )

Cabinet Simulation
------------------

A real guitar amp doesn't just distort the signal -- the speaker
cabinet shapes the tone dramatically. A 12-inch speaker in a closed
cabinet rolls off the harsh high frequencies above 5 kHz and adds a
presence bump around 2--3 kHz that gives the sound its "in the room"
quality. Without a cabinet, distortion sounds thin and fizzy. With
one, it sounds like a real amp.

PyTheory's cabinet simulation applies a speaker rolloff curve (lowpass
at ~5 kHz) combined with a presence resonance bump, placed in the
signal chain immediately after distortion -- exactly where it sits in
a real amp.

Parameters:

- ``cabinet``: Wet/dry mix, 0.0--1.0 (default 0, off).

  - 0.3--0.5 = subtle speaker coloring
  - 0.6--0.8 = classic amp-in-a-room
  - 1.0 = full cabinet, no dry signal

.. code-block:: python

   # Classic rock amp tone: distortion into cabinet
   guitar = score.part(
       "guitar",
       synth="saw",
       envelope="pluck",
       distortion=0.6,
       distortion_drive=5.0,
       cabinet=0.8,
   )

   # Clean amp with just cabinet warmth (no distortion)
   clean = score.part(
       "clean",
       synth="triangle",
       envelope="pluck",
       cabinet=0.5,
   )

Analog Drift
------------

Real analog synthesizers are never perfectly in tune. The voltage-
controlled oscillators drift slightly over time as components warm up
and temperature fluctuates. This imperfection is actually a big part
of why vintage analog synths sound so appealing -- the subtle pitch
wandering gives each note a unique, living quality that static digital
oscillators lack.

The ``analog_drift`` parameter adds slow, random pitch variation to
each oscillator, modeling this vintage behavior.

Parameters:

- ``analog_drift``: Drift amount, 0.0--1.0 (default 0, off).

  - 0.05--0.1 = subtle warmth (studio-grade analog)
  - 0.15--0.25 = noticeable drift (vintage gear warming up)
  - 0.3+ = unstable, wobbly (broken tape machine)

.. code-block:: python

   # Warm vintage pad
   pad = score.part(
       "pad",
       synth="supersaw",
       envelope="pad",
       analog_drift=0.1,
       chorus=0.3,
   )

   # Lo-fi detuned lead
   lead = score.part(
       "lead",
       synth="saw",
       envelope="pluck",
       analog_drift=0.25,
   )

Chorus
------

That shimmery, wide, slightly-out-of-focus sound that defined the
1980s? That's chorus. Think of the intro to "Come As You Are" by
Nirvana, or literally any synth pad from 1983 to 1989. It makes one
instrument sound like two or three playing together, slightly out of
tune with each other -- which is exactly how a real string section or
choir sounds rich and full.

A slightly detuned, LFO-modulated delayed copy mixed back in. Thickens
the sound like two musicians playing the same part -- the signature
effect of the Roland Juno synthesizers.

Parameters:

- ``chorus``: Wet/dry mix, 0.0--1.0.
- ``chorus_rate``: LFO speed in Hz. 0.5--1 = slow shimmer, 2--4 = vibrato.
- ``chorus_depth``: Modulation depth in seconds (default 0.003).

.. code-block:: python

   # Juno-style pad chorus
   pad = score.part(
       "pad",
       synth="supersaw",
       envelope="pad",
       chorus=0.5,
       chorus_rate=1.5,
       chorus_depth=0.003,
   )

   # Subtle thickening on a clean lead
   lead = score.part(
       "lead",
       synth="triangle",
       envelope="pluck",
       chorus=0.2,
       chorus_rate=0.8,
   )

Lowpass Filter
--------------

You know that sound when a DJ turns the knob and everything goes
underwater? That's a lowpass filter closing down. It removes
high-frequency content, leaving only the warm, round, bassy
frequencies below the cutoff point. The lowpass filter is arguably the
most important effect in all of electronic music -- it's the entire
sound of acid house, the "wah" in auto-wah, and the reason analog
synths sound warm instead of harsh.

A 12 dB/octave biquad lowpass filter with resonance -- the sound of
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

.. code-block:: python

   # Round bass with gentle filtering
   bass = score.part(
       "bass",
       synth="sine",
       envelope="pluck",
       lowpass=400,
       lowpass_q=1.5,
   )

   # Acid squelch on a saw lead
   acid = score.part(
       "acid",
       synth="saw",
       envelope="staccato",
       lowpass=1500,
       lowpass_q=5.0,
       legato=True,
       glide=0.03,
   )

Delay
-----

Delay is echo. Literally. The Edge from U2 built his entire guitar
sound around dotted-eighth-note delays. Dub reggae producers like Lee
"Scratch" Perry and King Tubby turned delay into an art form, feeding
echoes back into themselves until they spiraled into infinity. At short
times with low feedback, delay adds rhythmic interest. At long times
with high feedback, it creates cascading, psychedelic soundscapes.

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

.. code-block:: python

   # Dotted-eighth slapback on a lead
   lead = score.part(
       "lead",
       synth="triangle",
       envelope="strings",
       delay=0.3,
       delay_time=0.375,
       delay_feedback=0.4,
   )

   # Dub-style runaway echoes
   melodica = score.part(
       "melodica",
       synth="triangle",
       envelope="pluck",
       delay=0.5,
       delay_time=0.66,
       delay_feedback=0.55,
   )

Reverb
------

Everyone knows what reverb sounds like, even if they don't know the
word -- it's the sound of singing in the shower, or clapping in a
cathedral. It's the natural echo of a space. Without reverb, sounds
feel uncomfortably close and dry, like someone whispering directly into
your ear. With it, sounds feel like they exist in a real place. Reverb
is the most universally used effect in all of recorded music.

PyTheory offers two reverb engines: a fast **algorithmic** reverb for
general use, and **convolution** reverb for photorealistic acoustic
spaces.

Algorithmic Reverb
~~~~~~~~~~~~~~~~~~

A Schroeder reverb using 4 parallel comb filters and 2 series allpass
filters. Fast, lightweight, and good for general-purpose room
simulation.

Parameters:

- ``reverb``: Wet/dry mix, 0.0--1.0.

  - 0.2--0.4 = subtle space
  - 0.5--0.8 = ambient / dub

- ``reverb_decay``: Tail length in seconds.

  - 0.5 = small room
  - 1.5 = hall
  - 3.0+ = cathedral / dub

.. code-block:: python

   # Jazz club ambience
   rhodes = score.part(
       "rhodes",
       synth="fm",
       envelope="piano",
       reverb=0.4,
       reverb_decay=1.8,
   )

Convolution Reverb
~~~~~~~~~~~~~~~~~~

Convolution reverb works by convolving your audio with an *impulse
response* -- a recording (or simulation) of a real acoustic space.
Where algorithmic reverb approximates the math of reflections,
convolution reverb *is* the space. You hear every surface, every
angle, every material.

PyTheory generates synthetic impulse responses that model the acoustic
properties of real spaces: early reflection patterns, exponential
decay envelopes, frequency-dependent absorption (high frequencies die
faster in stone), diffusion density, and subtle pitch modulation from
irregular surfaces. The result is dramatically more realistic than
algorithmic reverb, especially for long tails and large spaces.

Set ``reverb_type`` to any preset name instead of ``"algorithmic"``:

- ``"taj_mahal"`` -- Massive marble dome. 12-second tail, bright early
  reflections, enormously dense and diffuse. The most dramatic verb
  you've ever heard.
- ``"cathedral"`` -- Gothic stone cathedral. 6 seconds, strong early
  reflections off parallel walls, dark reverberant tail.
- ``"plate"`` -- EMT 140 plate reverb. 4 seconds, dense, bright, smooth.
  The studio classic that defined pop records from the 60s onward.
- ``"spring"`` -- Spring reverb tank. 3 seconds, metallic, boingy, lo-fi.
  The sound of surf rock and guitar amps.
- ``"cave"`` -- Natural cave. 8 seconds, very dark, irregular reflections.
  High frequencies are aggressively absorbed by rock.
- ``"parking_garage"`` -- Concrete box. 3 seconds, bright, flutter echoes
  from parallel hard walls.
- ``"canyon"`` -- Open canyon. 5 seconds, sparse discrete echoes (the
  walls are far apart) dissolving into a diffuse tail.

Parameters:

- ``reverb``: Wet/dry mix, 0.0--1.0.
- ``reverb_type``: Preset name (default ``"algorithmic"``).

.. code-block:: python

   # FM flute through the Taj Mahal
   flute = score.part(
       "flute",
       synth="fm",
       envelope="bell",
       reverb=0.85,
       reverb_type="taj_mahal",
       delay=0.65,
       delay_time=0.375,
       delay_feedback=0.55,
   )

   # Cathedral wash for ambient pads
   pad = score.part(
       "pad",
       synth="supersaw",
       envelope="pad",
       reverb=0.7,
       reverb_type="cathedral",
   )

   # Classic plate on a vocal-style lead
   lead = score.part(
       "lead",
       synth="triangle",
       envelope="strings",
       reverb=0.5,
       reverb_type="plate",
   )

   # Algorithmic reverb still works as before
   rhodes = score.part(
       "rhodes",
       synth="fm",
       envelope="piano",
       reverb=0.4,
       reverb_decay=1.8,
   )

You can switch reverb types mid-song with automation:

.. code-block:: python

   lead = score.part("lead", synth="fm", envelope="bell",
                     reverb=0.5, reverb_type="plate")
   lead.add("C5", Duration.WHOLE)

   # Switch to cathedral for the big section
   lead.set(reverb_type="cathedral", reverb=0.8)
   lead.add("E5", Duration.WHOLE)

Combining Effects
-----------------

Effects stack naturally. Here are some real-world combinations:

Dub
~~~

Distortion warmth into filtered delay into deep reverb:

.. code-block:: python

   melodica = score.part(
       "melodica",
       synth="triangle",
       envelope="pluck",
       distortion=0.2,
       distortion_drive=2.0,
       lowpass=2000,
       lowpass_q=1.2,
       delay=0.5,
       delay_time=0.66,
       delay_feedback=0.55,
       reverb=0.4,
       reverb_decay=2.5,
   )

Acid
~~~~

Resonant lowpass with distortion and delay:

.. code-block:: python

   acid = score.part(
       "acid",
       synth="saw",
       envelope="staccato",
       lowpass=1500,
       lowpass_q=3.0,
       distortion=0.4,
       distortion_drive=4.0,
       delay=0.3,
       delay_time=0.242,
       delay_feedback=0.4,
   )

Ambient
~~~~~~~

Wide chorus, long reverb, gentle delay:

.. code-block:: python

   ambient = score.part(
       "ambient",
       synth="supersaw",
       envelope="pad",
       chorus=0.4,
       chorus_rate=0.5,
       delay=0.3,
       delay_time=0.5,
       delay_feedback=0.5,
       reverb=0.7,
       reverb_decay=4.0,
   )

808 Bass
~~~~~~~~

Subtle saturation and deep filtering for hip-hop sub bass:

.. code-block:: python

   bass = score.part(
       "bass",
       synth="sine",
       envelope="pluck",
       lowpass=200,
       lowpass_q=1.8,
       distortion=0.4,
       distortion_drive=2.0,
   )

Sidechain Compression
---------------------

If you've ever heard a house track where the pad *breathes* — gets
quiet every time the kick hits and swells back up between beats —
that's sidechain compression. It's the pumping effect that defines
modern electronic music. The kick drum triggers a compressor on
another part, ducking its volume in rhythm with the beat.

In PyTheory, the drum hits are the trigger. Any part with
``sidechain > 0`` gets ducked whenever the kick (or any drum) hits:

.. code-block:: python

   # Classic EDM pump — pad ducks hard on every kick
   pad = score.part(
       "pad",
       synth="supersaw",
       envelope="pad",
       sidechain=0.85,
       sidechain_release=0.15,
   )

   # Bass breathes with the kick too, but less aggressively
   bass = score.part(
       "bass",
       synth="sine",
       lowpass=250,
       sidechain=0.7,
       sidechain_release=0.1,
   )

Parameters:

- ``sidechain``: How much to duck, 0.0–1.0 (default 0, off).
  0.5 = subtle pump, 0.7 = noticeable, 0.85 = classic EDM, 1.0 = full silence on hits.
- ``sidechain_release``: How fast the volume comes back, in seconds
  (default 0.1). Shorter = tighter, longer = more dramatic pump.

The lead stays above the pump — don't sidechain everything or the
whole mix will gasp for air:

.. code-block:: python

   # Lead cuts through — no sidechain
   lead = score.part(
       "lead",
       synth="saw",
       envelope="pluck",
       delay=0.2,
   )

Saturation
----------

Saturation is the warm, subtle harmonic enhancement of analog tape
machines and tube preamps. Unlike distortion (which uses ``tanh`` and
adds harsh odd harmonics), saturation uses a polynomial waveshaper
that adds even harmonics -- 2nd and 4th -- which the ear perceives as
warmth and fullness. It's why records mixed through a Neve console
sound "bigger" than the same mix done in the box.

Parameters:

- ``saturation``: Amount, 0.0--1.0 (default 0, off).

  - 0.05--0.15 = subtle analog warmth (tape machine)
  - 0.2--0.4 = noticeable color (tube preamp)
  - 0.5+ = heavy coloring

.. code-block:: python

   # Warm up a bass
   bass = score.part("bass", synth="saw", saturation=0.2)

   # Glue a string ensemble
   strings = score.part("strings", instrument="string_ensemble",
                        saturation=0.1)

Tremolo
-------

Amplitude modulation by a sine LFO. The classic vibrating-amp sound.
Essential for vibraphone (the rotating discs in the resonator tubes),
Rhodes electric piano, and surf guitar. Not to be confused with
vibrato (pitch modulation).

Parameters:

- ``tremolo_depth``: Modulation depth, 0.0--1.0 (default 0, off).
- ``tremolo_rate``: LFO speed in Hz (default 5.0).

  - 3--5 Hz = classic tremolo
  - 5--7 Hz = vibraphone motor speed
  - 8+ Hz = ring-mod territory

.. code-block:: python

   # Classic Fender amp tremolo
   guitar = score.part("guitar", synth="saw", envelope="pluck",
                       tremolo_depth=0.3, tremolo_rate=4.0)

   # Vibraphone with motor
   vib = score.part("vib", instrument="vibraphone")  # built in

Phaser
------

A chain of allpass filters whose center frequencies are swept by an
LFO, creating moving notches in the spectrum. The classic "jet
engine" or "underwater" effect. Think Small Stone, MXR Phase 90, or
the intro to "Eruption." Different from chorus -- chorus adds a
detuned copy, phaser cancels specific frequencies.

Parameters:

- ``phaser``: Wet/dry mix, 0.0--1.0 (default 0, off).
- ``phaser_rate``: LFO sweep speed in Hz (default 0.5).

  - 0.1--0.3 = slow, lush sweep
  - 0.5--1.0 = classic phaser
  - 2.0+ = fast, Leslie-like

.. code-block:: python

   # Slow sweep on a pad
   pad = score.part("pad", synth="supersaw", envelope="pad",
                    phaser=0.4, phaser_rate=0.2)

   # Leslie sim on organ (built in)
   organ = score.part("organ", instrument="organ")

Highpass Filter
---------------

The opposite of lowpass -- removes low-frequency content below the
cutoff. Useful for cleaning up mud from pads, keeping multiple bass
parts from masking each other, or thinning out a sound to sit better
in a mix.

Parameters:

- ``highpass``: Cutoff frequency in Hz (0 = off).

  - 80--150 Hz = clean up sub rumble
  - 200--400 Hz = thin out a pad
  - 500+ Hz = telephone / radio effect

- ``highpass_q``: Resonance / Q factor (default 0.707).

.. code-block:: python

   # Clean up sub rumble from a pad
   pad = score.part("pad", synth="supersaw", highpass=120)

   # Thin out rhythm guitar to leave room for bass
   rhythm = score.part("rhythm", synth="saw", highpass=250)

Filter Envelope
---------------

A per-note lowpass filter whose cutoff sweeps over time. This is the
core of subtractive synthesis -- the reason a Moog bass goes "bwow"
instead of "boop." The filter opens on the attack and closes during
decay, giving each note a distinctive timbral shape.

Parameters:

- ``filter_amount``: Sweep range in Hz (0 = off). How far the filter
  opens above the base cutoff.
- ``filter_attack``: Time to reach peak cutoff, in seconds (default 0.01).
- ``filter_decay``: Time to fall to sustain level (default 0.3).
- ``filter_sustain``: Sustain level as fraction of amount, 0.0--1.0
  (default 0.0 = filter closes completely after decay).

.. code-block:: python

   # Classic synth bass "bwow"
   bass = score.part("bass", instrument="synth_bass")  # built in

   # Acid squelch
   acid = score.part("acid", instrument="acid_bass")  # built in

   # Custom filter sweep on a lead
   lead = score.part("lead", synth="saw",
                     filter_amount=4000, filter_attack=0.01,
                     filter_decay=0.4, filter_sustain=0.1)

Velocity to Brightness
~~~~~~~~~~~~~~~~~~~~~~

Real instruments get brighter when played harder. ``vel_to_filter``
maps note velocity to filter cutoff boost, so louder notes have more
high-frequency content.

- ``vel_to_filter``: Cutoff boost in Hz at max velocity (default 0, off).

.. code-block:: python

   # Piano: soft = mellow, loud = bright
   piano = score.part("piano", instrument="piano")  # built in

   # Manual: custom velocity mapping on a lead
   lead = score.part("lead", synth="saw", vel_to_filter=3000)

Sub-Oscillator
--------------

An octave-below sine wave mixed in with the main oscillator. Adds
low-end weight without muddiness -- the sub fills in the fundamental
while the main oscillator provides harmonic character above.

- ``sub_osc``: Mix level, 0.0--1.0 (default 0, off).

  - 0.1--0.2 = subtle weight (tuba, bass guitar)
  - 0.3--0.5 = heavy sub (808, synth bass)

.. code-block:: python

   # Fat 808 kick-bass
   bass = score.part("bass", instrument="808_bass")  # built in

   # Add weight to any part
   lead = score.part("lead", synth="saw", sub_osc=0.3)

Noise Layer
-----------

White noise mixed into each note, following the same amplitude
envelope. Adds breath for woodwinds, hammer/felt noise for piano,
bow rosin for strings, and attack transients for percussion.

- ``noise_mix``: Mix level, 0.0--1.0 (default 0, off).

  - 0.02--0.04 = subtle texture (strings, piano)
  - 0.05--0.08 = noticeable breath (woodwinds)
  - 0.1+ = heavy air/texture

.. code-block:: python

   # Breathy flute
   flute = score.part("flute", instrument="flute")  # noise_mix=0.08

   # Add air to any synth
   pad = score.part("pad", synth="supersaw", noise_mix=0.05)

Configurable FM
---------------

The FM synth now accepts ``fm_ratio`` and ``fm_index`` parameters,
letting you dial in specific FM timbres instead of using the defaults.

- ``fm_ratio``: Modulator frequency as multiple of carrier (default 2.0).
  Integer ratios = harmonic timbres; non-integer = metallic/inharmonic.
- ``fm_index``: Modulation depth (default 3.0). Higher = more harmonics.

.. code-block:: python

   # Warm electric piano (low ratio, low index)
   ep = score.part("ep", synth="fm", fm_ratio=1.0, fm_index=1.5)

   # Bright metallic bell (high ratio, high index)
   bell = score.part("bell", synth="fm", fm_ratio=3.5, fm_index=5.0)

   # Glockenspiel
   glock = score.part("glock", instrument="glockenspiel")  # built in

Automation
----------

Static effects are fine for a loop, but music breathes. The filter
*opens* during the chorus. The reverb *swells* before the drop. The
distortion *kicks in* when the guitar solo starts. Automation is what
makes a track feel alive instead of robotic -- it's the difference
between a static loop and a piece of music that has dynamics, tension,
and release. If you've ever felt a song "build" toward something,
you're hearing automation at work.

``Part.set()`` changes effect parameters mid-song at the current beat
position. The renderer splits the audio at automation points and
processes each section independently:

.. code-block:: python

   lead = score.part("lead", synth="saw", lowpass=400, lowpass_q=3.0)

   # Verse: filtered and clean
   lead.arpeggio("Cm", bars=4, pattern="up", octaves=2)

   # Chorus: filter opens, chorus kicks in
   lead.set(lowpass=2000, chorus=0.3)
   lead.arpeggio("Fm", bars=4, pattern="updown", octaves=2)

   # Drop: full send
   lead.set(lowpass=4000, distortion=0.7, reverb=0.3)
   lead.arpeggio("Gm", bars=4, pattern="updown", octaves=2)

Any parameter can be automated: ``lowpass``, ``lowpass_q``, ``highpass``,
``reverb``, ``reverb_decay``, ``delay``, ``delay_time``, ``delay_feedback``,
``distortion``, ``distortion_drive``, ``chorus``, ``phaser``, ``phaser_rate``,
``saturation``, ``tremolo_depth``, ``tremolo_rate``, ``volume``.

LFO Automation
--------------

An LFO -- Low Frequency Oscillator -- is just automation that repeats.
Instead of manually setting parameter changes, you let a wave shape do
it for you, cycling back and forth continuously. You already know what
LFOs sound like, even if you don't know the term. The wobble bass in
dubstep? That's an LFO on the filter cutoff. Tremolo on a guitar amp?
LFO on volume. Auto-wah? LFO on filter cutoff with resonance cranked
up. Vibrato? LFO on pitch. It's one simple concept that produces a
huge range of effects.

``Part.lfo()`` automates a parameter with a low-frequency oscillator,
generating smooth sweeps over time. This is how filter sweeps, tremolo,
and auto-wah effects work.

.. code-block:: python

   lead = score.part("lead", synth="saw", lowpass=400)

   # Slow filter sweep: 400 -> 3000 Hz over 8 bars
   lead.lfo("lowpass", rate=0.125, min=400, max=3000, bars=8)
   lead.arpeggio("Cm", bars=8, pattern="up", octaves=2)

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

.. code-block:: python

   lead = score.part("lead", synth="saw", lowpass=800, reverb=0.1)

   # Filter opens over 8 bars
   lead.lfo("lowpass", rate=0.125, min=400, max=4000, bars=8)
   # Reverb swells in and out every 2 bars
   lead.lfo("reverb", rate=0.5, min=0.1, max=0.6, bars=8, shape="triangle")
   # Volume tremolo
   lead.lfo("volume", rate=2, min=0.3, max=0.6, bars=8, shape="sine")

   lead.arpeggio("Cm", bars=8, pattern="updown", octaves=2)

Effects are what turn notes into music -- the space, the movement, the character. A dry signal is just information; reverb, delay, and filtering are what make it feel like something. Experiment freely, trust your ears.
