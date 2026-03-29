"""Real-time MIDI-driven synthesis engine.

Listens for MIDI input (e.g. from an OP-XY, keyboard, or DAW) and
synthesizes audio in real-time through pytheory's synth engine.

Usage::

    from pytheory.live import LiveEngine

    engine = LiveEngine()
    engine.channel(1, instrument="electric_piano")
    engine.channel(2, instrument="bass_guitar", lowpass=800)
    engine.channel(10, drums=True)
    engine.start()  # blocks until Ctrl-C
"""

import threading
import numpy
import sounddevice as sd
import rtmidi

from .play import (
    _SYNTH_FUNCTIONS, _resolve_synth, _resolve_envelope,
    _apply_envelope, _apply_lowpass, _render_drum_hit_cached,
    SAMPLE_RATE, SAMPLE_PEAK,
)
from .rhythm import INSTRUMENTS, DrumSound


# ── Voice ────────────────────────────────────────────────────────────────

class _Voice:
    """A single sounding note — holds a pre-rendered wavetable and
    tracks playback position + envelope state."""
    __slots__ = ('wave', 'pos', 'velocity', 'active', 'releasing',
                 'release_pos', 'release_len', 'note')

    def __init__(self, wave, velocity, note):
        self.wave = wave           # float32 array — one shot or looped
        self.pos = 0               # current read position
        self.velocity = velocity
        self.active = True
        self.releasing = False
        self.release_pos = 0
        self.release_len = int(SAMPLE_RATE * 0.05)  # 50ms release
        self.note = note           # MIDI note number


# ── Channel ──────────────────────────────────────────────────────────────

class _Channel:
    """One MIDI channel — has a synth, effects, and a voice pool."""

    def __init__(self, synth_name="sine", envelope_name="piano",
                 is_drums=False, max_voices=12, **kwargs):
        self.synth_fn = _resolve_synth(synth_name)
        self.synth_name = synth_name
        self.envelope_name = envelope_name
        self.env_tuple = _resolve_envelope(envelope_name)
        self.is_drums = is_drums
        self.max_voices = max_voices
        self.kwargs = kwargs
        self.lowpass = kwargs.get('lowpass', 0)
        self.lowpass_q = kwargs.get('lowpass_q', 0.707)
        self.reverb = kwargs.get('reverb', 0)
        self.volume = kwargs.get('volume', 0.5)

        self.voices = []           # active _Voice objects
        self._cache = {}           # MIDI note → pre-rendered wave
        self._lock = threading.Lock()

    def _get_wave(self, midi_note, n_samples):
        """Get or render a waveform for a MIDI note."""
        if self.is_drums:
            return _render_drum_hit_cached(midi_note, n_samples)

        if midi_note in self._cache:
            cached = self._cache[midi_note]
            if len(cached) >= n_samples:
                return cached[:n_samples]

        hz = 440.0 * (2 ** ((midi_note - 69) / 12.0))

        # Synth kwargs
        skw = {}
        if self.synth_name in ("fm",):
            skw["mod_ratio"] = self.kwargs.get("fm_ratio", 2.0)
            skw["mod_index"] = self.kwargs.get("fm_index", 3.0)

        wave = self.synth_fn(hz, n_samples=n_samples, **skw)
        wave_f = wave.astype(numpy.float32) / SAMPLE_PEAK

        # Apply envelope
        a, d, s, r = self.env_tuple
        if a > 0 or d > 0 or s < 1.0 or r > 0:
            wave_f = _apply_envelope(wave_f, a, d, s, r)

        # Apply lowpass
        if self.lowpass > 0:
            wave_f = _apply_lowpass(wave_f, self.lowpass, q=self.lowpass_q)

        self._cache[midi_note] = wave_f
        return wave_f

    def note_on(self, midi_note, velocity):
        """Start a new voice."""
        vel_scale = velocity / 127.0
        # Render 2 seconds of audio
        n_samples = SAMPLE_RATE * 2
        wave = self._get_wave(midi_note, n_samples)

        with self._lock:
            # Voice stealing — kill oldest if at max
            if len(self.voices) >= self.max_voices:
                self.voices.pop(0)
            self.voices.append(_Voice(wave, vel_scale, midi_note))

    def note_off(self, midi_note):
        """Trigger release on voices playing this note."""
        with self._lock:
            for v in self.voices:
                if v.note == midi_note and v.active and not v.releasing:
                    v.releasing = True
                    v.release_pos = 0

    def render(self, n_frames):
        """Mix all active voices into a buffer."""
        buf = numpy.zeros(n_frames, dtype=numpy.float32)
        dead = []

        with self._lock:
            for i, v in enumerate(self.voices):
                if not v.active:
                    dead.append(i)
                    continue

                remaining = len(v.wave) - v.pos
                chunk = min(n_frames, remaining)

                if chunk <= 0:
                    v.active = False
                    dead.append(i)
                    continue

                samples = v.wave[v.pos:v.pos + chunk] * v.velocity * self.volume

                # Release fade
                if v.releasing:
                    fade_chunk = min(chunk, v.release_len - v.release_pos)
                    if fade_chunk > 0:
                        fade = numpy.linspace(
                            1.0 - v.release_pos / v.release_len,
                            1.0 - (v.release_pos + fade_chunk) / v.release_len,
                            fade_chunk
                        ).astype(numpy.float32)
                        samples[:fade_chunk] *= fade
                        v.release_pos += fade_chunk
                    if v.release_pos >= v.release_len:
                        v.active = False
                        samples[fade_chunk:] = 0

                buf[:chunk] += samples
                v.pos += chunk

            # Clean up dead voices
            for i in reversed(dead):
                if i < len(self.voices):
                    self.voices.pop(i)

        return buf


# ── LiveEngine ───────────────────────────────────────────────────────────

class LiveEngine:
    """Real-time MIDI-to-audio engine.

    Maps MIDI channels to pytheory instruments and synthesizes
    audio in real-time via sounddevice.

    Example::

        engine = LiveEngine()
        engine.channel(1, instrument="electric_piano")
        engine.channel(2, instrument="bass_guitar")
        engine.channel(10, drums=True)
        engine.start()
    """

    def __init__(self, buffer_size=512, sample_rate=SAMPLE_RATE):
        self.buffer_size = buffer_size
        self.sample_rate = sample_rate
        self.channels = {}   # MIDI channel (1-16) → _Channel
        self._midi_in = None
        self._stream = None

    def channel(self, ch, *, instrument=None, synth=None, envelope=None,
                drums=False, **kwargs):
        """Configure a MIDI channel.

        Args:
            ch: MIDI channel number (1-16). Channel 10 = drums by convention.
            instrument: Instrument preset name (e.g. "electric_piano").
            synth: Synth waveform name (overrides instrument).
            envelope: Envelope name (overrides instrument).
            drums: If True, this channel triggers drum sounds by MIDI note.
            **kwargs: Any Part parameter (lowpass, reverb, volume, etc.)
        """
        # Build params from instrument preset
        params = {}
        if instrument:
            preset = INSTRUMENTS.get(instrument)
            if preset:
                params.update(preset)
        if synth:
            params["synth"] = synth
        if envelope:
            params["envelope"] = envelope
        params.update(kwargs)

        synth_name = params.pop("synth", "sine")
        env_name = params.pop("envelope", "piano")

        self.channels[ch] = _Channel(
            synth_name=synth_name,
            envelope_name=env_name,
            is_drums=drums or ch == 10,
            **params,
        )
        return self

    def _midi_callback(self, event, data=None):
        """Handle incoming MIDI messages."""
        msg, _ = event
        if len(msg) < 3:
            return

        status = msg[0]
        ch = (status & 0x0F) + 1  # MIDI channels are 0-indexed in protocol
        msg_type = status & 0xF0

        if ch not in self.channels:
            return

        channel = self.channels[ch]
        note = msg[1]
        velocity = msg[2]

        if msg_type == 0x90 and velocity > 0:
            channel.note_on(note, velocity)
        elif msg_type == 0x80 or (msg_type == 0x90 and velocity == 0):
            channel.note_off(note)

    def _audio_callback(self, outdata, frames, time_info, status):
        """sounddevice callback — mix all channels."""
        buf = numpy.zeros(frames, dtype=numpy.float32)
        for channel in self.channels.values():
            buf += channel.render(frames)

        # Soft clip
        buf = numpy.tanh(buf)

        # Stereo output
        outdata[:, 0] = buf
        outdata[:, 1] = buf

    def list_ports(self):
        """List available MIDI input ports."""
        midi_in = rtmidi.MidiIn()
        ports = midi_in.get_ports()
        for i, name in enumerate(ports):
            print(f"  {i}: {name}")
        midi_in.delete()
        return ports

    def start(self, port=None):
        """Start the engine — opens MIDI input and audio output.

        Args:
            port: MIDI port index or name. None = first available.

        Blocks until Ctrl-C.
        """
        if not self.channels:
            # Default: Rhodes on channel 1
            self.channel(1, instrument="electric_piano")

        # Open MIDI
        self._midi_in = rtmidi.MidiIn()
        ports = self._midi_in.get_ports()

        if not ports:
            print("  No MIDI input ports found.")
            print("  Connect a MIDI device and try again.")
            return

        if port is None:
            port = 0
        elif isinstance(port, str):
            for i, name in enumerate(ports):
                if port.lower() in name.lower():
                    port = i
                    break

        self._midi_in.open_port(port)
        self._midi_in.set_callback(self._midi_callback)
        port_name = ports[port] if isinstance(port, int) else port

        print(f"  PyTheory Live Engine")
        print(f"  MIDI: {port_name}")
        print(f"  Buffer: {self.buffer_size} samples ({self.buffer_size/self.sample_rate*1000:.1f}ms)")
        print(f"  Channels:")
        for ch, channel in sorted(self.channels.items()):
            kind = "drums" if channel.is_drums else channel.synth_name
            print(f"    {ch:2d}: {kind} (vol={channel.volume})")
        print()
        print("  Playing... (Ctrl-C to stop)")
        print()

        # Open audio
        self._stream = sd.OutputStream(
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            channels=2,
            dtype='float32',
            callback=self._audio_callback,
        )

        try:
            self._stream.start()
            # Block forever
            threading.Event().wait()
        except KeyboardInterrupt:
            print("\n  Stopped.")
        finally:
            self._stream.stop()
            self._stream.close()
            self._midi_in.close_port()
            self._midi_in.delete()

    def stop(self):
        """Stop the engine."""
        if self._stream:
            self._stream.stop()
        if self._midi_in:
            self._midi_in.close_port()
