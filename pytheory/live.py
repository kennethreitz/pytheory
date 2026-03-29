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

Note: sustained notes are pre-rendered to a 3-second wavetable.
Instruments requiring longer sustain (pads, organ) will cut off
after 3 seconds. This is a known limitation of the current
wavetable approach.
"""

import threading
import numpy
import sounddevice as sd

try:
    import rtmidi
except ImportError:
    rtmidi = None

from .play import (
    _SYNTH_FUNCTIONS, _resolve_synth, _resolve_envelope,
    _apply_envelope, _apply_lowpass, _render_drum_hit_cached,
    SAMPLE_RATE, SAMPLE_PEAK,
)
from .rhythm import INSTRUMENTS, DrumSound


# ── Voice ────────────────────────────────────────────────────────────────

class _Voice:
    """A single sounding note - holds a pre-rendered wavetable and
    tracks playback position + envelope state."""
    __slots__ = ('active', 'note', 'pitch_ratio', 'pos', 'release_len',
                 'release_pos', 'releasing', 'velocity', 'wave')

    def __init__(self, wave, velocity, note):
        self.wave = wave           # float32 array - one shot
        self.pos = 0.0             # current read position (float for pitch bend)
        self.velocity = velocity
        self.active = True
        self.releasing = False
        self.release_pos = 0
        self.release_len = int(SAMPLE_RATE * 0.05)  # 50ms release
        self.note = note           # MIDI note number
        self.pitch_ratio = 1.0     # 1.0 = normal, >1 = up, <1 = down


# ── Channel ──────────────────────────────────────────────────────────────

class _Channel:
    """One MIDI channel - has a synth, effects, and a voice pool."""

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
        self._cache = {}           # MIDI note -> pre-rendered wave
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

        # Apply reverb - simple feedback delay for real-time
        if self.reverb > 0:
            wet = self.reverb
            delay_samples = int(SAMPLE_RATE * 0.03)  # 30ms early reflection
            delay2 = int(SAMPLE_RATE * 0.047)        # second tap
            delay3 = int(SAMPLE_RATE * 0.071)        # third tap
            reverbed = wave_f.copy()
            for delay, gain in [(delay_samples, 0.4), (delay2, 0.3), (delay3, 0.2)]:
                if delay < len(reverbed):
                    reverbed[delay:] += wave_f[:-delay] * gain
            # Feedback loop for tail
            fb_delay = int(SAMPLE_RATE * 0.05)
            feedback = 0.35
            for _ in range(6):
                if fb_delay < len(reverbed):
                    reverbed[fb_delay:] += reverbed[:-fb_delay] * feedback
                    feedback *= 0.7
                    fb_delay = int(fb_delay * 1.5)
            wave_f = wave_f * (1.0 - wet) + reverbed * wet

        self._cache[midi_note] = wave_f
        return wave_f

    def note_on(self, midi_note, velocity):
        """Start a new voice."""
        vel_scale = velocity / 127.0
        # Render 3 seconds of audio (extra for reverb tail)
        n_samples = SAMPLE_RATE * 3
        wave = self._get_wave(midi_note, n_samples)

        with self._lock:
            # Voice stealing - kill oldest if at max
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

                remaining = len(v.wave) - int(v.pos)
                chunk = min(n_frames, remaining)

                if chunk <= 0:
                    v.active = False
                    dead.append(i)
                    continue

                # Pitch bend: read at variable rate through the wavetable
                if abs(v.pitch_ratio - 1.0) > 0.001:
                    read_positions = v.pos + numpy.arange(chunk) * v.pitch_ratio
                    read_positions = numpy.clip(read_positions, 0, len(v.wave) - 2)
                    idx = read_positions.astype(numpy.int64)
                    frac = (read_positions - idx).astype(numpy.float32)
                    samples = (v.wave[idx] * (1 - frac) + v.wave[numpy.minimum(idx + 1, len(v.wave) - 1)] * frac)
                    samples *= v.velocity * self.volume
                else:
                    int_pos = int(v.pos)
                    samples = v.wave[int_pos:int_pos + chunk] * v.velocity * self.volume

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
                v.pos += chunk * v.pitch_ratio

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
        self.channels = {}   # MIDI channel (1-16) -> _Channel
        self._cc_map = {}    # (channel, cc_number) -> (param_name, min, max)
        self._midi_in = None
        self._stream = None
        self._stop_event = threading.Event()
        # Clock sync
        self._clock_count = 0      # MIDI clock pulses (24 per quarter note)
        self._clock_times = []     # timestamps for BPM calculation
        self._bpm = 120.0
        self._playing = False
        # Drum pattern
        self._drum_pattern = None
        self._drum_channel = None

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
        if not isinstance(ch, int) or not (1 <= ch <= 16):
            raise ValueError(f"MIDI channel must be an integer 1-16, got {ch!r}")

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

    def drums(self, pattern_name, *, volume=0.5):
        """Add a drum pattern that syncs to MIDI clock.

        The pattern plays in sync with the OP-XY's transport -
        starts on Start, stops on Stop, tempo from MIDI clock.

        Args:
            pattern_name: Drum pattern preset name (e.g. "rock", "house").
            volume: Drum volume (0.0-1.0).
        """
        from .rhythm import Pattern
        self._drum_pattern = Pattern.preset(pattern_name)
        self._drum_channel = _Channel(synth_name="sine", is_drums=True,
                                      volume=volume)
        return self

    def cc(self, cc_number, param, *, min_val=0.0, max_val=1.0, ch=None):
        """Map a MIDI CC to a channel parameter.

        Args:
            cc_number: MIDI CC number (0-127).
            param: Parameter name ("volume", "lowpass", "reverb", etc.)
            min_val: Value when CC = 0.
            max_val: Value when CC = 127.
            ch: MIDI channel (None = all channels).

        Example::

            >>> engine.cc(11, "lowpass", min_val=200, max_val=8000)
            >>> engine.cc(12, "volume", min_val=0.0, max_val=1.0)
            >>> engine.cc(13, "reverb", min_val=0.0, max_val=0.8)
            >>> engine.cc(14, "distortion", min_val=0.0, max_val=0.8)
        """
        self._cc_map[(ch, cc_number)] = (param, min_val, max_val)
        return self

    def _apply_cc(self, ch, cc_number, value):
        """Apply a CC value to the matching channel parameter."""
        for key in [(ch, cc_number), (None, cc_number)]:
            if key in self._cc_map:
                param, min_val, max_val = self._cc_map[key]
                scaled = min_val + (max_val - min_val) * (value / 127.0)

                target_chs = [ch] if key[0] is not None else list(self.channels.keys())
                for target_ch in target_chs:
                    if target_ch in self.channels:
                        channel = self.channels[target_ch]
                        if param == "volume":
                            channel.volume = scaled
                        elif param == "lowpass":
                            channel.lowpass = scaled
                            channel._cache.clear()
                        elif param == "reverb":
                            channel.reverb = scaled
                            channel._cache.clear()
                        elif hasattr(channel, param):
                            setattr(channel, param, scaled)
                            channel._cache.clear()
                        print(f"  CC {cc_number}: {param}={scaled:.2f}")
                return

    def _on_clock(self):
        """Handle MIDI clock pulse (24 per quarter note)."""
        import time as _time

        if not self._playing:
            return

        now = _time.perf_counter()
        self._clock_times.append(now)
        if len(self._clock_times) > 48:
            self._clock_times = self._clock_times[-48:]
        if len(self._clock_times) >= 24:
            interval = (self._clock_times[-1] - self._clock_times[-24]) / 24
            if interval > 0:
                self._bpm = 60.0 / interval

        # Trigger drum hits at the right time
        if self._drum_pattern and self._drum_channel:
            pattern = self._drum_pattern
            beat_pos = self._clock_count / 24.0
            pattern_beat = beat_pos % pattern.beats
            beat_resolution = 1.0 / 24.0
            for hit in pattern.hits:
                if abs(hit.position - pattern_beat) < beat_resolution / 2:
                    self._drum_channel.note_on(hit.sound.value, hit.velocity)

        self._clock_count += 1

    def _all_notes_off(self):
        """Kill all sounding voices on all channels."""
        for channel in self.channels.values():
            with channel._lock:
                channel.voices.clear()
        if self._drum_channel:
            with self._drum_channel._lock:
                self._drum_channel.voices.clear()

    def _midi_callback(self, event, data=None):
        """Handle incoming MIDI messages."""
        msg, _ = event
        if len(msg) == 0:
            return

        # System realtime messages (1 byte)
        if msg[0] == 0xF8:  # Clock - 24 ppqn
            self._on_clock()
            return
        elif msg[0] == 0xFA:  # Start
            print("  > Start")
            self._playing = True
            self._clock_count = 0
            return
        elif msg[0] == 0xFC:  # Stop
            print("  [] Stop")
            self._playing = False
            self._all_notes_off()
            return
        elif msg[0] == 0xFB:  # Continue
            print("  > Continue")
            self._playing = True
            return

        if len(msg) < 3:
            return

        status = msg[0]
        ch = (status & 0x0F) + 1
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
        elif msg_type == 0xB0:
            self._apply_cc(ch, note, velocity)
        elif msg_type == 0xE0:
            bend_raw = (msg[2] << 7) | msg[1]
            bend_semitones = (bend_raw - 8192) / 8192.0 * 2.0
            ratio = 2.0 ** (bend_semitones / 12.0)
            with channel._lock:
                for v in channel.voices:
                    if v.active:
                        v.pitch_ratio = ratio

    def _audio_callback(self, outdata, frames, time_info, status):
        """sounddevice callback - mix all channels."""
        buf = numpy.zeros(frames, dtype=numpy.float32)
        for channel in self.channels.values():
            buf += channel.render(frames)
        if self._drum_channel:
            buf += self._drum_channel.render(frames)

        buf = numpy.tanh(buf)
        outdata[:, 0] = buf
        outdata[:, 1] = buf

    def list_ports(self):
        """List available MIDI input ports."""
        if rtmidi is None:
            raise ImportError("python-rtmidi required. Install with: pip install pytheory[live]")
        midi_in = rtmidi.MidiIn()
        ports = midi_in.get_ports()
        for i, name in enumerate(ports):
            print(f"  {i}: {name}")
        midi_in.delete()
        return ports

    def start(self, port=None):
        """Start the engine - opens MIDI input and audio output.

        Args:
            port: MIDI port index or name. None = first available.

        Blocks until Ctrl-C or stop() is called.
        """
        if rtmidi is None:
            raise ImportError(
                "python-rtmidi is required for live MIDI. "
                "Install it with: pip install pytheory[live]"
            )

        if not self.channels:
            self.channel(1, instrument="electric_piano")

        # Pre-compute wavetables
        print("  Pre-rendering wavetables...")
        n_samples = SAMPLE_RATE * 3
        for _, channel in self.channels.items():
            if channel.is_drums:
                continue
            for midi_note in range(36, 97):
                channel._get_wave(midi_note, n_samples)
        print(f"  Cached {sum(len(c._cache) for c in self.channels.values())} wavetables.")
        print()

        # Open MIDI
        self._midi_in = rtmidi.MidiIn()
        ports = self._midi_in.get_ports()

        if not ports:
            print("  No MIDI input ports found.")
            print("  Connect a MIDI device and try again.")
            self._midi_in.delete()
            self._midi_in = None
            return

        if port is None:
            port = 0
        elif isinstance(port, str):
            matched = False
            for i, name in enumerate(ports):
                if port.lower() in name.lower():
                    port = i
                    matched = True
                    break
            if not matched:
                self._midi_in.delete()
                self._midi_in = None
                raise ValueError(f"MIDI input port not found: {port!r}")

        try:
            self._midi_in.open_port(port)
        except Exception:
            self._midi_in.delete()
            self._midi_in = None
            raise

        self._midi_in.ignore_types(sysex=True, timing=False, active_sense=True)
        self._midi_in.set_callback(self._midi_callback)
        port_name = ports[port]

        print(f"  PyTheory Live Engine")
        print(f"  MIDI: {port_name}")
        print(f"  Buffer: {self.buffer_size} samples ({self.buffer_size/self.sample_rate*1000:.1f}ms)")
        print(f"  Channels:")
        for ch, channel in sorted(self.channels.items()):
            kind = "drums" if channel.is_drums else channel.synth_name
            print(f"    {ch:2d}: {kind} (vol={channel.volume})")
        if self._drum_pattern:
            print(f"  Drums: {self._drum_pattern.name} (synced to MIDI clock)")
        print()
        print("  Playing... (Ctrl-C to stop)")
        print()

        self._stream = sd.OutputStream(
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            channels=2,
            dtype='float32',
            callback=self._audio_callback,
        )

        try:
            self._stream.start()
            self._stop_event.clear()
            self._stop_event.wait()
        except KeyboardInterrupt:
            print("\n  Stopped.")
        finally:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            self._midi_in.close_port()
            self._midi_in.delete()
            self._midi_in = None

    def stop(self):
        """Stop the engine."""
        self._stop_event.set()
        if self._stream:
            self._stream.stop()
        if self._midi_in:
            self._midi_in.close_port()
            self._midi_in.delete()
            self._midi_in = None
