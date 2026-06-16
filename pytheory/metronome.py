"""A metronome and tempo trainer.

PyTheory already knows about tempo and can synthesize sound, so a
metronome falls out almost for free. This module adds three things:

- a plain metronome (accented downbeat, optional subdivisions),
- a **practice mode** that clicks while cycling through a chord
  progression — one chord per bar, softly under the click, and
- a **tempo trainer** that ramps the tempo over time (start BPM →
  end BPM, stepping by a set amount every so many beats), the way
  the phone apps do it.

Everything streams in real time through ``sounddevice``::

    >>> from pytheory.metronome import Metronome
    >>> Metronome(bpm=120, beats=4).start()                  # plain click
    >>> Metronome(bpm=90, progression=["Am", "F", "C", "G"]).start()
    >>> Metronome(bpm=80, end_bpm=120, step=4, every=8).start()  # trainer
"""
from __future__ import annotations

import numpy

from .play import SAMPLE_RATE, SAMPLE_PEAK


# Click pitches (Hz). The downbeat is the brightest, weaker beats sit a
# little lower, and subdivisions are lower and quieter still — the usual
# high/low metronome split.
_ACCENT_HZ = 1568.0   # G6 — the "one"
_BEAT_HZ = 988.0      # B5 — the other beats
_SUB_HZ = 784.0       # G5 — subdivisions ("and"s)


def _click(freq: float, *, length: float = 0.045, volume: float = 0.7):
    """Synthesize a single metronome tick as a float32 mono buffer."""
    n = int(SAMPLE_RATE * length)
    t = numpy.arange(n, dtype=numpy.float64) / SAMPLE_RATE
    # A fast-decaying sine, with a tiny noise transient for the "tick".
    body = numpy.sin(2 * numpy.pi * freq * t) * numpy.exp(-t * 55.0)
    attack = int(SAMPLE_RATE * 0.002)
    transient = numpy.zeros(n)
    if attack:
        transient[:attack] = (numpy.random.uniform(-1.0, 1.0, attack)
                              * numpy.exp(-numpy.linspace(0, 9, attack)))
    wave = (body + transient * 0.4) * volume
    return wave.astype(numpy.float32)


class Metronome:
    """A real-time metronome, practice click, and tempo trainer.

    Args:
        bpm: Starting tempo in beats per minute (default 120).
        beats: Beats per bar — the time signature's top number
            (default 4).
        accent: If True, accent the downbeat of each bar (default True).
        subdivide: Clicks per beat — ``1`` for quarter notes, ``2`` for
            eighths, ``3`` for triplets, ``4`` for sixteenths (default 1).
        progression: Optional chord symbols (e.g. ``["Am", "F", "C",
            "G"]``) to play softly under the click, one chord per bar,
            looping. Turns the metronome into a chord-practice tool.
        chord_synth: Waveform for the chord stab (default ``"triangle"``).
        chord_volume: Level of the chord stab relative to the click
            (default 0.35).
        end_bpm: If set, ramp the tempo from ``bpm`` toward this value —
            the tempo-trainer mode.
        step: BPM change applied at each ramp step (default 5).
        every: Number of beats between ramp steps (default 8 — two bars
            of 4/4).
        hold: When the trainer reaches ``end_bpm``, keep clicking at that
            tempo if True, otherwise stop (default True).
    """

    def __init__(self, bpm: float = 120, beats: int = 4, *,
                 accent: bool = True, subdivide: int = 1,
                 progression=None, chord_synth: str = "triangle",
                 chord_volume: float = 0.35,
                 end_bpm: float | None = None, step: float = 5,
                 every: int = 8, hold: bool = True) -> None:
        if bpm <= 0:
            raise ValueError("bpm must be positive")
        if beats < 1:
            raise ValueError("beats must be at least 1")
        if subdivide < 1:
            raise ValueError("subdivide must be at least 1")
        self.bpm = float(bpm)
        self.beats = beats
        self.accent = accent
        self.subdivide = subdivide
        self.progression = list(progression) if progression else None
        self.chord_synth = chord_synth
        self.chord_volume = chord_volume
        self.end_bpm = float(end_bpm) if end_bpm is not None else None
        self.step = abs(step)
        self.every = max(1, every)
        self.hold = hold

        # Pre-rendered clicks (tempo-independent).
        self._accent = _click(_ACCENT_HZ, volume=0.85)
        self._beat = _click(_BEAT_HZ, volume=0.6)
        self._sub = _click(_SUB_HZ, length=0.03, volume=0.3)
        self._chord_cache: dict[str, numpy.ndarray] = {}

    # ── buffer construction ──────────────────────────────────────────

    def _chord_stab(self, symbol: str, length: int) -> numpy.ndarray:
        """Render a chord to a soft, decaying stab of ``length`` samples."""
        from .chords import Chord
        from .play import _render, Synth, Envelope

        key = f"{symbol}@{length}"
        if key in self._chord_cache:
            return self._chord_cache[key]
        try:
            chord = Chord.from_symbol(symbol)
        except (ValueError, KeyError):
            stab = numpy.zeros(length, dtype=numpy.float32)
            self._chord_cache[key] = stab
            return stab
        synth = Synth[self.chord_synth.upper()]
        ms = int(length / SAMPLE_RATE * 1000)
        raw = _render(chord, synth=synth, t=ms, envelope=Envelope.PLUCK)
        stab = raw.astype(numpy.float32) / SAMPLE_PEAK * self.chord_volume
        if len(stab) < length:
            stab = numpy.pad(stab, (0, length - len(stab)))
        else:
            stab = stab[:length]
        self._chord_cache[key] = stab
        return stab

    def _bar(self, symbol: str | None) -> numpy.ndarray:
        """Build one bar of audio at the current tempo."""
        beat_len = int(SAMPLE_RATE * 60.0 / self.bpm)
        bar = numpy.zeros(beat_len * self.beats, dtype=numpy.float32)

        sub_len = beat_len / self.subdivide
        for b in range(self.beats):
            for s in range(self.subdivide):
                pos = int(b * beat_len + s * sub_len)
                if s != 0:
                    click = self._sub
                elif b == 0 and self.accent:
                    click = self._accent
                else:
                    click = self._beat
                end = min(pos + len(click), len(bar))
                bar[pos:end] += click[:end - pos]

        if symbol:
            bar += self._chord_stab(symbol, len(bar))

        # Keep headroom so the click stays crisp and never clips.
        peak = float(numpy.max(numpy.abs(bar))) if bar.size else 0.0
        if peak > 0.95:
            bar *= 0.95 / peak
        return bar

    # ── playback ─────────────────────────────────────────────────────

    def start(self, *, on_bar=None) -> None:
        """Start clicking. Blocks until the trainer finishes or Ctrl-C.

        Args:
            on_bar: Optional callback ``on_bar(bar_index, bpm, symbol)``
                invoked at the top of each bar (used by the CLI to print
                a status line; handy for custom UIs too).
        """
        import sounddevice as sd

        bar_index = 0
        beats_elapsed = 0
        ramping = self.end_bpm is not None and self.end_bpm != self.bpm
        # Steps accumulate from a fixed origin so rounding never compounds.
        origin = self.bpm
        direction = 1.0 if (ramping and self.end_bpm > origin) else -1.0

        reached = False  # played a bar at the target yet?
        with sd.OutputStream(samplerate=SAMPLE_RATE, channels=1,
                             dtype="float32") as stream:
            try:
                while True:
                    symbol = None
                    if self.progression:
                        symbol = self.progression[bar_index % len(self.progression)]
                    if on_bar is not None:
                        on_bar(bar_index, round(self.bpm, 1), symbol)

                    stream.write(self._bar(symbol))

                    bar_index += 1
                    beats_elapsed += self.beats

                    if reached:  # the target bar just played — done
                        break
                    if ramping:
                        steps = beats_elapsed // self.every
                        new_bpm = origin + direction * self.step * steps
                        if direction > 0:
                            new_bpm = min(new_bpm, self.end_bpm)
                        else:
                            new_bpm = max(new_bpm, self.end_bpm)
                        self.bpm = new_bpm
                        # Let one bar sound at the target before stopping.
                        if self.bpm == self.end_bpm and not self.hold:
                            reached = True
            except KeyboardInterrupt:
                pass
