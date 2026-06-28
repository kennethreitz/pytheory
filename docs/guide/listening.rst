Listening — Microphone In
=========================

Everything else in PyTheory goes *out* — to speakers, MIDI, sheet
music. This page is the other direction: PyTheory listens. Hum a
melody into your phone and get back notes you can edit. Drop a song
in and get a four-part arrangement sketch. Plug in nothing at all
and tune your guitar.

Three tools, one pipeline (the YIN pitch tracker, implemented in
pure numpy):

- **Transcription** — ``Score.from_wav("hum.m4a")`` turns a recording
  into an editable Score.
- **Studio** — ``pytheory studio``, the same thing as a drag-and-drop
  browser page with sheet music and playback.
- **The tuner** — ``pytheory tune``, real-time pitch with a strobe
  display in your browser — and with ``--chords``, it names the
  chord you're strumming.

Audio Import — WAV → Score
--------------------------

Record yourself humming a melody, whistling a hook, or playing a
bass line, and turn the recording back into notes you can edit,
harmonize, quantize, export to MIDI, or print as sheet music:

.. code-block:: python

   from pytheory import Score

   score = Score.from_wav("hum.wav", bpm=100, quantize=0.25)

   for note in score.parts["melody"].notes:
       print(note.tone, note.beats)

   score.save_midi("hum.mid")          # finish it in your DAW
   print(score.to_abc(title="My Hum")) # or print the sheet music

Pitch tracking uses the YIN algorithm — the same approach as most
monophonic tuners — implemented in pure numpy. Transcription is
**monophonic**: one note at a time (voice, whistle, a single
instrument line), not chords. Record melody and bass as separate
takes.

For full mixes, pass ``split=True`` and you get a **full arrangement
sketch** back — four parts plus the key:

.. code-block:: python

   from pytheory import Score, play_score

   score = Score.from_wav("song.wav", split=True, quantize=0.5)

   score.parts["melody"]    # the lead line
   score.parts["bass"]      # the bassline
   score.parts["chords"]    # chord voicings (Am, F, C, G...)
   score.parts["drums"]     # kick / snare / hat hits
   score.detected_key       # e.g. <Key C major>

   play_score(score)        # an instant cover version

The ``melody`` and ``bass`` parts always come back; ``chords`` and
``drums`` show up only when there's harmony or percussion to find.

Under the hood: harmonic-percussive separation splits sustained
pitched material from drums (held notes are horizontal lines on a
spectrogram, drum hits vertical ones — median filters tell them
apart). The harmonic stem gets band-split YIN passes for bass and
melody, plus a **chromagram** — the spectrum folded into 12 pitch
classes — matched against major/minor/sus triad and 7th-chord
templates per chord window. The window grid aligns itself to the
music's own onsets (so a pickup bar doesn't smear every chord
across two windows), and when the bass sits steadily on a chord
tone that isn't the root, you get the inversion as a slash chord
(``C/E``). The percussive stem gets onset detection with each hit
classified as kick, snare, or hat by where its energy lives. The
key falls out of everything pitched via :meth:`Key.detect`.

What to expect: chords and bassline come out well (a rendered
Am-F-C-G test mix comes back exactly), the melody as well as it
dominates the mix, and the drum groove reads correctly even when
individual edge hits get fuzzy. It's a sketch to edit, not a record
deal — but it turns "what is this song?" into an editable Score in
one line.

Tempo is estimated automatically when you don't pass ``bpm=`` — the
onset pattern is autocorrelated to find the pulse (a rendered groove
comes back exact; pulse-free rubato humming falls back to 120).

Every stage of that pipeline is a public function, so you can wire
up your own: :func:`~pytheory.audio.hpss` (the harmonic/percussive
split), :func:`~pytheory.audio.detect_pitch` (the YIN tracker),
:func:`~pytheory.audio.estimate_tempo`,
:func:`~pytheory.audio.detect_chords`, and
:func:`~pytheory.audio.detect_drums`.

Tips for good transcriptions:

- **Tighten the pitch range** — ``fmin=60, fmax=350`` for a bass
  line, ``fmin=150, fmax=1200`` for whistling. Less range to search
  means fewer octave mistakes.
- **Raise the floor above vocal fry** — voice recordings often carry
  low creaky artifacts at note starts and ends that transcribe as
  quiet sub-bass blips. If you see suspiciously low, low-velocity
  notes at phrase boundaries, set ``fmin=100`` (or higher) and they
  disappear.
- **Pin the tempo if you know it** — auto-estimation reads the pulse
  from the onsets, but if you recorded against a metronome, pass
  that ``bpm=`` and remove the guesswork.
- **Quantize when you want a clean chart** — ``quantize=0.25`` snaps
  to sixteenths; leave it off to keep the timing as performed.

Phone voice memos (.m4a), mp3s, and other formats load directly —
they're converted on the fly through ``afconvert`` (built into
macOS) or ``ffmpeg``, whichever is on your PATH.

There's a CLI command too::

   $ pytheory transcribe hum.m4a hum.mid --quantize 0.25
   $ pytheory transcribe bass.wav --fmin 60 --fmax 350 --play
   $ pytheory transcribe song.wav --split

See the :doc:`cookbook` for the full voice-memo-to-sheet-music
recipe.

PyTheory Studio — the Browser Front Door
----------------------------------------

All of the above, without writing any code::

   $ pytheory studio

opens a local web app at ``http://localhost:8124``: **drop in a
recording** (.wav, voice memo, .mp3) and the transcription renders
as sheet music right on the page
(via abcjs). Press play to hear it through PyTheory's synths,
download the MIDI for your DAW, and there's a tuner at the bottom.
Check "full mix" for the four-part bass/melody/chords/drums split.

Everything runs on your machine — the only thing fetched from the
internet is the notation renderer. Your audio never leaves localhost.

The Tuner
---------

Every musician needs a tuner, and you already have a microphone.
PyTheory's tuner tracks your pitch live (same YIN algorithm as the
transcriber) and shows the note plus how many cents sharp or flat
you are::

   $ pytheory tune
     A4  ----------------------------●------ +12.3¢ ( 443.14 Hz)

Tuning a guitar? Tell it, and readings lock to the nearest open
string — tuning the D string never gets misread as "80 cents flat
of E"::

   $ pytheory tune --instrument guitar
     → D3 ------------------●---------------  -8.1¢ ( 146.15 Hz)

Presets: guitar, bass, ukulele, violin, viola, cello, mandolin,
banjo.

For the full strobe-tuner experience, serve it to your browser::

   $ pytheory tune --serve

That opens ``http://localhost:8123`` — a strobe display (the
segmented disc drifts clockwise when you're sharp, counter-clockwise
when you're flat, and freezes when you're dead on — the same logic
as a Peterson strobe), plus a needle, and your instrument's strings
highlighted as you hit them with ``--instrument``.

The page is fed by a **Server-Sent Events stream at** ``/stream``
(CORS open) and the same stream over **WebSocket at** ``/ws`` —
which means any JavaScript app can tap PyTheory's pitch detection
directly, no client library required:

.. code-block:: javascript

   const tuner = new EventSource("http://localhost:8123/stream");
   tuner.onmessage = (e) => {
       const reading = JSON.parse(e.data);
       if (reading) {
           // { freq: 146.15, note: "D", octave: 3,
           //   cents: -8.1, in_tune: false, target: "D3" }
           updateMyUI(reading);
       }
   };

   // or: new WebSocket("ws://localhost:8123/ws")

Build your own tuner page, drive a game, pitch-train an ear-training
app — the stream doesn't care what's listening.

Orchestras tuning high? ``pytheory tune --ref 442``. More than one
microphone? ``--device N`` picks the input by index. Python access is
:class:`pytheory.tuner.Tuner` (``tuner.reading`` holds the latest
analysis; pass ``instrument="cello"`` for string targets) and
:func:`pytheory.tuner.analyze_frame` for one-shot use.

Chord Recognition
-----------------

The tuner can also name what you're *strumming*::

   $ pytheory tune --serve --chords

Play a chord and the page shows its symbol and tones — ``Am  A C E``
— above the tuner. It recognizes major, minor, sus2/sus4, and 7th
chords on all twelve roots, and it knows the difference between a
chord and a single note (a lone note just gets the normal tuner
readout). Works in the terminal too: ``pytheory tune --chords``.

In chord mode the SSE/WebSocket stream carries three extra fields —
``chord`` (the symbol, or ``null``), ``chord_notes``, and
``chord_confidence`` — so a JS app can listen for chords the same
way it listens for pitch.

The analysis is :func:`pytheory.audio.identify_chord`: a chromagram
of the last second of audio, with each pitch class discounted by the
harmonic spill it receives from the others (a bright C major puts
real energy on B — the 3rd partial of its E — which is what makes
naive matchers cry "Cmaj7"), matched against chord templates on all
twelve roots. You can call it yourself on any buffer:

.. code-block:: python

   from pytheory.audio import load_wav, identify_chord

   samples, sr = load_wav("strum.wav")
   identify_chord(samples, sr)
   # {'symbol': 'Am', 'confidence': 0.98, 'notes': ['A', 'C', 'E']}

One honest physics note: an instrument's low single notes carry
their harmonics' pitch classes, so an open low E string played alone
can occasionally read as an E chord — the polyphony gate catches
most of these, but it can't beat Fourier. Strum two more strings.

What Next
---------

A transcription is an ordinary :class:`~pytheory.rhythm.Score` — so
everything in :doc:`sequencing` applies: change synths, add parts,
layer drums. Reharmonize or analyze what came back with the tools in
:doc:`chords`, export it via :doc:`playback`, and if you play the
result live, that's :doc:`live`.
