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

Notes are pre-rendered to a 3-second wavetable. Sustaining
instruments (organ, pads, strings — any envelope with a nonzero
sustain level) loop seamlessly inside the wavetable, so held keys
ring for as long as you hold them. Percussive instruments (piano,
plucks) decay naturally and end.

Effects (lowpass, reverb, chorus, delay, tremolo, distortion,
saturation) run on each channel's bus in real time, so MIDI CC
sweeps are smooth and instant — no wavetable re-rendering.

To play in time with Ableton Live, iOS apps, or anything else that
speaks Ableton Link (requires ``pip install pytheory[link]``)::

    engine.enable_link()
    engine.start()

Tempo, the drum-pattern beat grid, and transport start/stop all
sync with the Link session — peer-to-peer, no master.
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


# Parameters baked into pre-rendered wavetables — changing one of these
# requires clearing the channel's cache. Everything else streams on the
# channel bus and updates instantly.
_BAKED_PARAMS = frozenset({'detune', 'sub_osc', 'noise_mix'})


# ── Voice ────────────────────────────────────────────────────────────────

class _Voice:
    """A single sounding note - holds a pre-rendered wavetable and
    tracks playback position + envelope state."""
    __slots__ = ('active', 'loop_end', 'loop_start', 'note', 'pitch_ratio',
                 'pos', 'release_len', 'release_pos', 'releasing',
                 'velocity', 'wave')

    def __init__(self, wave, velocity, note, loop_start=None, loop_end=None):
        self.wave = wave           # float32 array
        self.pos = 0.0             # current read position (float for pitch bend)
        self.velocity = velocity
        self.active = True
        self.releasing = False
        self.release_pos = 0
        self.release_len = int(SAMPLE_RATE * 0.05)  # 50ms release
        self.note = note           # MIDI note number
        self.pitch_ratio = 1.0     # 1.0 = normal, >1 = up, <1 = down
        self.loop_start = loop_start  # sustain loop region (None = one-shot)
        self.loop_end = loop_end


class _StreamReverb:
    """Streaming Schroeder reverb — state persists across audio blocks.

    Same topology and tuning as the offline reverb in play.py (4
    parallel feedback combs + 2 series allpasses), but processable
    one buffer at a time. Comb feedback never recurses within a
    block (delays exceed typical block sizes; longer blocks are
    chunked), so each block is pure vectorized ring-buffer reads.
    """
    COMB_DELAY_SECS = (0.0297, 0.0371, 0.0411, 0.0437)
    ALLPASS_DELAY_SECS = (0.005, 0.0017)

    def __init__(self, decay=1.0, sample_rate=SAMPLE_RATE):
        self.combs = []
        for d_sec in self.COMB_DELAY_SECS:
            d = int(d_sec * sample_rate)
            gain = 0.001 ** (d / sample_rate / decay)
            # [ring buffer of u where u[t] = x[t] + g*u[t-D], write pos, gain]
            self.combs.append([numpy.zeros(d, dtype=numpy.float32), 0, gain])
        self.allpasses = []
        for d_sec in self.ALLPASS_DELAY_SECS:
            d = int(d_sec * sample_rate)
            b = numpy.zeros(d + 1); b[0] = -0.7; b[d] = 1.0
            a = numpy.zeros(d + 1); a[0] = 1.0; a[d] = -0.7
            self.allpasses.append([b, a, numpy.zeros(d)])

    def process(self, x):
        """Process one block; returns the wet signal."""
        from scipy.signal import lfilter
        wet = numpy.zeros(len(x), dtype=numpy.float32)
        for state in self.combs:
            ring, pos, gain = state
            d = len(ring)
            out = numpy.empty(len(x), dtype=numpy.float32)
            i = 0
            while i < len(x):
                m = min(d, len(x) - i)
                idx = (pos + numpy.arange(m)) % d
                u_old = ring[idx]              # u[t-D], which is y[t]
                ring[idx] = x[i:i + m] + gain * u_old
                out[i:i + m] = u_old
                pos = (pos + m) % d
                i += m
            state[1] = pos
            wet += out
        wet /= len(self.combs)
        for state in self.allpasses:
            b, a, zi = state
            wet, state[2] = lfilter(b, a, wet, zi=zi)
        return wet.astype(numpy.float32)


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
        self.pan = kwargs.get('pan', 0.0)  # -1 left, 0 center, 1 right
        self.chorus = kwargs.get('chorus', 0)
        self.detune = kwargs.get('detune', 0)
        self.spread = kwargs.get('spread', 0)
        self.analog = kwargs.get('analog', 0)
        self.distortion = kwargs.get('distortion', 0)
        self.delay = kwargs.get('delay', 0)
        self.tremolo_depth = kwargs.get('tremolo_depth', 0)
        self.saturation = kwargs.get('saturation', 0)
        self.phaser = kwargs.get('phaser', 0)
        self.sub_osc = kwargs.get('sub_osc', 0)
        self.noise_mix = kwargs.get('noise_mix', 0)

        self.voices = []           # active _Voice objects
        self._cache = {}           # MIDI note -> (wave, loop_start, loop_end)
        self._lock = threading.Lock()
        self.level = 0.0           # current output level (for VU meter)

        # Streaming effect state — effects run on the channel bus per
        # audio block, so parameter changes (MIDI CC, TUI fx commands)
        # take effect instantly without re-rendering wavetables.
        self._lp_zi = numpy.zeros(2)
        self._lp_coeffs = None              # (cutoff, q, b, a)
        self._trem_phase = 0.0
        self._chorus_ring = numpy.zeros(int(SAMPLE_RATE * 0.08),
                                        dtype=numpy.float32)
        self._chorus_pos = 0
        self._chorus_phase = 0.0
        self._delay_ring = numpy.zeros(int(SAMPLE_RATE * 1.0),
                                       dtype=numpy.float32)
        self._delay_pos = 0
        self._reverb_state = None           # lazy _StreamReverb

    # Loop region inside the 3s wavetable for sustaining instruments.
    # Starts after attack+decay have settled, ends with margin to spare;
    # the region is crossfaded so the wrap is click-free.
    _LOOP_START = int(SAMPLE_RATE * 1.5)
    _LOOP_END = int(SAMPLE_RATE * 2.75)
    _LOOP_XFADE = 2048

    def _get_wave(self, midi_note, n_samples):
        """Get or render a wavetable. Returns (wave, loop_start, loop_end);
        loop points are None for one-shot (percussive/drum) sounds."""
        if self.is_drums:
            return _render_drum_hit_cached(midi_note, n_samples), None, None

        if midi_note in self._cache:
            wave_f, ls, le = self._cache[midi_note]
            if len(wave_f) >= n_samples:
                return wave_f, ls, le

        hz = 440.0 * (2 ** ((midi_note - 69) / 12.0))

        # Synth kwargs
        skw = {}
        if self.synth_name in ("fm",):
            skw["mod_ratio"] = self.kwargs.get("fm_ratio", 2.0)
            skw["mod_index"] = self.kwargs.get("fm_index", 3.0)

        wave = self.synth_fn(hz, n_samples=n_samples, **skw)
        wave_f = wave.astype(numpy.float32) / SAMPLE_PEAK

        # Detuned oscillator layers (oscillator-level, baked into the table)
        if self.detune > 0:
            up = self.synth_fn(hz * 2 ** (self.detune / 1200),
                               n_samples=n_samples, **skw)
            down = self.synth_fn(hz * 2 ** (-self.detune / 1200),
                                 n_samples=n_samples, **skw)
            wave_f = (wave_f + up.astype(numpy.float32) / SAMPLE_PEAK
                      + down.astype(numpy.float32) / SAMPLE_PEAK) / 3.0

        # Sub-oscillator (octave-below sine)
        if self.sub_osc > 0:
            t = numpy.arange(n_samples, dtype=numpy.float32) / SAMPLE_RATE
            sub = numpy.sin(2 * numpy.pi * (hz / 2) * t).astype(numpy.float32)
            wave_f = wave_f * (1.0 - self.sub_osc * 0.3) + sub * self.sub_osc * 0.3

        # Noise layer
        if self.noise_mix > 0:
            noise = numpy.random.uniform(-1, 1, n_samples).astype(numpy.float32)
            wave_f = (wave_f * (1.0 - self.noise_mix * 0.5)
                      + noise * self.noise_mix * 0.5)

        # Apply envelope
        a, d, s, r = self.env_tuple
        if a > 0 or d > 0 or s < 1.0 or r > 0:
            wave_f = _apply_envelope(wave_f, a, d, s, r)

        # Sustain loop — held notes ring indefinitely, but only for
        # genuinely sustaining instruments: the envelope must hold a
        # real level (organ/pad/strings) AND the source must still be
        # ringing at the loop region. Struck/plucked sources (piano,
        # guitar, mallets) decay on their own and stay one-shot.
        loop_start = loop_end = None
        if s >= 0.7 and n_samples > self._LOOP_END:
            early = numpy.sqrt(numpy.mean(
                wave_f[int(SAMPLE_RATE * 0.2):int(SAMPLE_RATE * 0.5)] ** 2))
            late = numpy.sqrt(numpy.mean(
                wave_f[self._LOOP_START:self._LOOP_START
                       + SAMPLE_RATE // 4] ** 2))
            if early > 0 and late > 0.3 * early:
                loop_start, loop_end = self._LOOP_START, self._LOOP_END
                xf = self._LOOP_XFADE
                fade = numpy.linspace(0.0, 1.0, xf, dtype=numpy.float32)
                wave_f[loop_end - xf:loop_end] = (
                    wave_f[loop_end - xf:loop_end] * (1 - fade)
                    + wave_f[loop_start - xf:loop_start] * fade)

        self._cache[midi_note] = (wave_f, loop_start, loop_end)
        return wave_f, loop_start, loop_end

    def note_on(self, midi_note, velocity):
        """Start a new voice."""
        vel_scale = velocity / 127.0
        n_samples = SAMPLE_RATE * 3
        wave, loop_start, loop_end = self._get_wave(midi_note, n_samples)

        with self._lock:
            # Voice stealing - kill oldest if at max
            if len(self.voices) >= self.max_voices:
                self.voices.pop(0)
            self.voices.append(_Voice(wave, vel_scale, midi_note,
                                      loop_start, loop_end))

    def note_off(self, midi_note):
        """Trigger release on voices playing this note."""
        with self._lock:
            for v in self.voices:
                if v.note == midi_note and v.active and not v.releasing:
                    v.releasing = True
                    v.release_pos = 0

    def render_stereo(self, n_frames):
        """Mix all active voices into a stereo buffer (n_frames, 2)."""
        mono = numpy.zeros(n_frames, dtype=numpy.float32)
        dead = []

        with self._lock:
            for i, v in enumerate(self.voices):
                if not v.active:
                    dead.append(i)
                    continue

                if v.loop_end is not None:
                    # Sustaining voice: read through the wavetable's
                    # crossfaded loop region — never runs out.
                    chunk = n_frames
                    span = v.loop_end - v.loop_start
                    positions = v.pos + numpy.arange(
                        chunk, dtype=numpy.float64) * v.pitch_ratio
                    over = positions >= v.loop_end
                    if over.any():
                        positions[over] = (v.loop_start
                                           + (positions[over] - v.loop_start)
                                           % span)
                    idx = positions.astype(numpy.int64)
                    frac = (positions - idx).astype(numpy.float32)
                    nxt = numpy.minimum(idx + 1, len(v.wave) - 1)
                    samples = (v.wave[idx] * (1 - frac) + v.wave[nxt] * frac)
                    samples *= v.velocity * self.volume
                    v.pos += chunk * v.pitch_ratio
                    if v.pos >= v.loop_end:
                        v.pos = v.loop_start + (v.pos - v.loop_start) % span
                else:
                    remaining = len(v.wave) - int(v.pos)
                    chunk = min(n_frames, remaining)

                    if chunk <= 0:
                        v.active = False
                        dead.append(i)
                        continue

                    # Pitch bend: variable-rate read
                    if abs(v.pitch_ratio - 1.0) > 0.001:
                        read_positions = v.pos + numpy.arange(chunk) * v.pitch_ratio
                        read_positions = numpy.clip(read_positions, 0, len(v.wave) - 2)
                        idx = read_positions.astype(numpy.int64)
                        frac = (read_positions - idx).astype(numpy.float32)
                        samples = (v.wave[idx] * (1 - frac) +
                                   v.wave[numpy.minimum(idx + 1, len(v.wave) - 1)] * frac)
                        samples *= v.velocity * self.volume
                    else:
                        int_pos = int(v.pos)
                        samples = v.wave[int_pos:int_pos + chunk] * v.velocity * self.volume
                    v.pos += chunk * v.pitch_ratio

                # Release crossfade
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

                mono[:chunk] += samples

            # Clean up dead voices
            for i in reversed(dead):
                if i < len(self.voices):
                    self.voices.pop(i)

        # Channel bus effects — streamed per block with persistent
        # state, so CC/TUI parameter changes apply instantly.
        mono = self._process_bus(mono)

        # VU meter
        peak = numpy.abs(mono).max() if len(mono) > 0 else 0
        self.level = self.level * 0.7 + peak * 0.3  # smooth

        # Stereo pan (constant power)
        import math
        angle = (self.pan + 1) * math.pi / 4  # 0 to pi/2
        l_gain = math.cos(angle)
        r_gain = math.sin(angle)
        stereo = numpy.zeros((n_frames, 2), dtype=numpy.float32)
        stereo[:, 0] = mono * l_gain
        stereo[:, 1] = mono * r_gain

        return stereo

    def _process_bus(self, mono):
        """Run the channel's effect chain on one audio block.

        Mirrors the offline signal chain (distortion → chorus →
        lowpass → delay → reverb) with tremolo/saturation alongside.
        All state (filter memory, delay lines, LFO phases) persists
        across blocks.
        """
        n = len(mono)
        if n == 0:
            return mono

        if self.distortion > 0:
            drive = 3.0
            mono = numpy.tanh(mono * drive * (1 + self.distortion * 3)) / drive
        if self.saturation > 0:
            mono = numpy.tanh(mono * (1 + self.saturation * 2))

        if self.tremolo_depth > 0:
            ph = (self._trem_phase
                  + 2 * numpy.pi * 5.0 * numpy.arange(n) / SAMPLE_RATE)
            mono = mono * (1.0 - self.tremolo_depth * 0.5
                           * (1 + numpy.sin(ph))).astype(numpy.float32)
            self._trem_phase = (ph[-1] + 2 * numpy.pi * 5.0 / SAMPLE_RATE) \
                % (2 * numpy.pi)

        if self.chorus > 0:
            ring = self._chorus_ring
            L = len(ring)
            t_idx = numpy.arange(n)
            w_idx = (self._chorus_pos + t_idx) % L
            ring[w_idx] = mono
            ph = (self._chorus_phase
                  + 2 * numpy.pi * 1.5 * t_idx / SAMPLE_RATE)
            delay = (0.007 + 0.003 * numpy.sin(ph)) * SAMPLE_RATE
            read = (self._chorus_pos + t_idx - delay) % L
            ri = read.astype(numpy.int64)
            frac = (read - ri).astype(numpy.float32)
            wet = ring[ri] * (1 - frac) + ring[(ri + 1) % L] * frac
            mono = mono * (1 - self.chorus * 0.5) + wet * self.chorus * 0.5
            self._chorus_phase = (ph[-1]
                                  + 2 * numpy.pi * 1.5 / SAMPLE_RATE) \
                % (2 * numpy.pi)
            self._chorus_pos = (self._chorus_pos + n) % L

        if self.lowpass > 0 and self.lowpass < SAMPLE_RATE / 2:
            from scipy.signal import lfilter
            key = (self.lowpass, self.lowpass_q)
            if self._lp_coeffs is None or self._lp_coeffs[0] != key:
                w0 = 2 * numpy.pi * self.lowpass / SAMPLE_RATE
                alpha = numpy.sin(w0) / (2 * self.lowpass_q)
                cos_w0 = numpy.cos(w0)
                a0 = 1 + alpha
                b = numpy.array([(1 - cos_w0) / 2, 1 - cos_w0,
                                 (1 - cos_w0) / 2]) / a0
                a = numpy.array([1.0, -2 * cos_w0 / a0, (1 - alpha) / a0])
                self._lp_coeffs = (key, b, a)
            _, b, a = self._lp_coeffs
            mono, self._lp_zi = lfilter(b, a, mono, zi=self._lp_zi)
            mono = mono.astype(numpy.float32)

        if self.delay > 0:
            ring = self._delay_ring
            L = len(ring)
            d = int(self.kwargs.get('delay_time', 0.375) * SAMPLE_RATE)
            d = max(n, min(d, L - 1))
            t_idx = numpy.arange(n)
            r_idx = (self._delay_pos + t_idx - d) % L
            wet = ring[r_idx].copy()
            feedback = self.kwargs.get('delay_feedback', 0.4)
            w_idx = (self._delay_pos + t_idx) % L
            ring[w_idx] = mono + wet * feedback
            mono = mono * (1 - self.delay) + wet * self.delay
            self._delay_pos = (self._delay_pos + n) % L

        if self.reverb > 0:
            if self._reverb_state is None:
                self._reverb_state = _StreamReverb(
                    decay=self.kwargs.get('reverb_decay', 1.0))
            wet = self._reverb_state.process(mono)
            mono = mono * (1 - self.reverb) + wet * self.reverb

        return mono.astype(numpy.float32)


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
        # Recording
        self._recording = False
        self._record_events = []   # (timestamp, ch, note, velocity, on/off)
        self._record_start = 0
        # Keyboard MIDI
        self._keyboard_channel = None
        self._keyboard_octave = 4
        # Clock sync
        self._clock_count = 0      # MIDI clock pulses (24 per quarter note)
        self._clock_times = []     # timestamps for BPM calculation
        self._bpm = 120.0
        self._playing = False
        # Ableton Link
        self._link = None
        self._link_quantum = 4.0
        self._link_start_stop = True
        self._link_last_beat = None
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
                        if hasattr(channel, param):
                            setattr(channel, param, scaled)
                            # Bus effects (lowpass, reverb, chorus, delay,
                            # tremolo, distortion...) pick up the new value
                            # on the next audio block. Only oscillator-level
                            # params baked into the wavetables need a
                            # re-render.
                            if param in _BAKED_PARAMS:
                                channel._cache.clear()
                return

    def enable_link(self, *, quantum=4.0, start_stop_sync=True):
        """Sync with an Ableton Link session on the local network.

        Tempo follows the session (and the session follows you —
        Link is peer-to-peer), the drum pattern locks to the shared
        beat grid, and transport start/stop syncs with peers that
        support it (Ableton Live, most iOS apps).

        Args:
            quantum: Bar length in beats for phase alignment
                (default 4 — drums land on the same downbeat as
                everyone else's bar).
            start_stop_sync: Follow Link transport start/stop.

        Requires the ``link`` extra::

            pip install pytheory[link]
        """
        try:
            import link as ablink
        except ImportError:
            raise ImportError(
                "LinkPython-extern is required for Ableton Link sync. "
                "Install it with: pip install pytheory[link]"
            ) from None
        self._link = ablink.Link(self._bpm)
        self._link_quantum = quantum
        self._link_start_stop = start_stop_sync
        self._link.startStopSyncEnabled = start_stop_sync
        self._link.setTempoCallback(self._on_link_tempo)
        if start_stop_sync:
            self._link.setStartStopCallback(self._on_link_start_stop)
        self._link.enabled = True
        return self

    def link_peers(self):
        """Number of Link peers currently on the network (0 if Link
        is not enabled)."""
        return self._link.numPeers() if self._link is not None else 0

    def _on_link_tempo(self, bpm):
        self._bpm = bpm

    def _on_link_start_stop(self, playing):
        self._playing = playing
        if not playing:
            self._all_notes_off()

    def _on_link_audio(self, frames):
        """Advance the Link beat grid by one audio block, triggering
        any drum hits the block crosses."""
        state = self._link.captureSessionState()
        now = self._link.clock().micros()
        tempo = state.tempo()
        if tempo > 10:
            self._bpm = tempo

        if self._link_start_stop and not state.isPlaying():
            self._link_last_beat = None
            return
        beat = state.beatAtTime(now, self._link_quantum)
        if beat < 0:                # count-in before the bar starts
            self._link_last_beat = None
            return

        last = self._link_last_beat
        self._link_last_beat = beat
        if last is None or beat < last:   # first block or beat jump
            last = max(0.0, beat - frames / self.sample_rate * tempo / 60.0)

        if not (self._drum_pattern and self._drum_channel):
            return
        pattern = self._drum_pattern
        b0 = last % pattern.beats
        b1 = b0 + (beat - last)
        for hit in pattern.hits:
            for pos in (hit.position, hit.position + pattern.beats):
                if b0 < pos <= b1:
                    self._drum_channel.note_on(hit.sound.value, hit.velocity)

    def _on_clock(self):
        """Handle MIDI clock pulse (24 per quarter note)."""
        import time as _time

        if self._link is not None:
            return  # Link owns tempo and the drum grid

        if not self._playing:
            return

        now = _time.perf_counter()
        self._clock_times.append(now)
        if len(self._clock_times) > 240:
            self._clock_times = self._clock_times[-240:]
        # Only update BPM every 24 ticks to avoid jitter
        if self._clock_count % 24 == 0 and len(self._clock_times) >= 48:
            # Use as many ticks as we have for best accuracy
            n = min(len(self._clock_times), 240)
            total_time = self._clock_times[-1] - self._clock_times[-n]
            if total_time > 0:
                ticks = n - 1
                self._bpm = round(60.0 * ticks / (24.0 * total_time))

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
            if self._recording:
                import time as _t
                self._record_events.append(
                    (_t.perf_counter() - self._record_start, ch, note, velocity, True))
        elif msg_type == 0x80 or (msg_type == 0x90 and velocity == 0):
            channel.note_off(note)
            if self._recording:
                import time as _t
                self._record_events.append(
                    (_t.perf_counter() - self._record_start, ch, note, 0, False))
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
        """sounddevice callback - mix all channels to stereo."""
        if self._link is not None:
            self._on_link_audio(frames)
        stereo = numpy.zeros((frames, 2), dtype=numpy.float32)
        for channel in self.channels.values():
            stereo += channel.render_stereo(frames)
        if self._drum_channel:
            stereo += self._drum_channel.render_stereo(frames)

        # Soft clip per channel
        stereo[:, 0] = numpy.tanh(stereo[:, 0])
        stereo[:, 1] = numpy.tanh(stereo[:, 1])
        outdata[:] = stereo

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
            print("  No MIDI input ports found. (Keyboard mode still works)")
            self._midi_in.delete()
            self._midi_in = None
            # Don't return — still start audio for keyboard mode

        port_name = "none"
        if self._midi_in and ports:
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
                    print(f"  MIDI port not found: {port!r}, continuing without MIDI")
                    port = None

            if self._midi_in and port is not None:
                try:
                    self._midi_in.open_port(port)
                    self._midi_in.ignore_types(sysex=True, timing=False, active_sense=True)
                    self._midi_in.set_callback(self._midi_callback)
                    port_name = ports[port]
                except Exception:
                    self._midi_in.delete()
                    self._midi_in = None
                    print("  Failed to open MIDI port, continuing without MIDI")

        print(f"  PyTheory Live Engine")
        print(f"  MIDI: {port_name}")
        print(f"  Buffer: {self.buffer_size} samples ({self.buffer_size/self.sample_rate*1000:.1f}ms)")
        print(f"  Channels:")
        for ch, channel in sorted(self.channels.items()):
            kind = "drums" if channel.is_drums else channel.synth_name
            print(f"    {ch:2d}: {kind} (vol={channel.volume})")
        if self._drum_pattern:
            sync = "Ableton Link" if self._link is not None else "MIDI clock"
            print(f"  Drums: {self._drum_pattern.name} (synced to {sync})")
        if self._link is not None:
            print(f"  Link: enabled — {self.link_peers()} peer(s), "
                  f"quantum {self._link_quantum:g}")
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
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            if self._midi_in:
                self._midi_in.close_port()
                self._midi_in.delete()
                self._midi_in = None

    def keyboard_play(self, ch=1):
        """Enable computer keyboard as MIDI input on a channel."""
        self._keyboard_channel = ch
        return self

    def keyboard_note(self, key, on=True):
        """Translate a keyboard key to a MIDI note and play it.

        QWERTY layout: ZSXDCVGBHNJM = C through B (lower octave)
                        Q2W3ER5T6Y7U = C through B (upper octave)
        """
        # Chromatic layout across the full keyboard
        # Bottom two rows = lower octave range
        # Top two rows = upper octave range (+1 octave)
        # Black keys on the row above their white keys
        #
        # Row 3 (ZXCVBNM,./): white keys C D E F G A B C D E
        # Row 2 (ASDFGHJKL;'): black keys + extras
        # Row 1 (QWERTYUIOP[]): white keys C D E F G A B C D E F G
        # Row 0 (1234567890-=): black keys + extras
        lower = {
            # White keys: Z X C V B N M , . /
            'z': 0, 'x': 2, 'c': 4, 'v': 5, 'b': 7, 'n': 9, 'm': 11,
            ',': 12, '.': 14, '/': 16,
            # Black keys: S D  G H J  L ;
            's': 1, 'd': 3, 'g': 6, 'h': 8, 'j': 10,
            'l': 13, ';': 15,
            # Extras
            'a': 0, 'f': 4, 'k': 11, "'": 17,
        }
        upper = {
            # White keys: Q W E R T Y U I O P [ ]
            'q': 0, 'w': 2, 'e': 4, 'r': 5, 't': 7, 'y': 9, 'u': 11,
            'i': 12, 'o': 14, 'p': 16, '[': 17, ']': 19,
            # Black keys: 2 3  5 6 7  9 0
            '2': 1, '3': 3, '5': 6, '6': 8, '7': 10,
            '9': 13, '0': 15,
            # Extras
            '1': 0, '4': 4, '8': 11, '-': 18, '=': 19,
        }

        if self._keyboard_channel is None:
            return False

        ch = self._keyboard_channel
        if ch not in self.channels:
            return False

        midi_note = None
        if key in lower:
            midi_note = (self._keyboard_octave + 1) * 12 + lower[key]
        elif key in upper:
            midi_note = (self._keyboard_octave + 2) * 12 + upper[key]

        if midi_note is not None:
            channel = self.channels[ch]
            if on:
                channel.note_on(midi_note, 100)
                if self._recording:
                    import time as _t
                    self._record_events.append(
                        (_t.perf_counter() - self._record_start,
                         ch, midi_note, 100, True))
            else:
                channel.note_off(midi_note)
                if self._recording:
                    import time as _t
                    self._record_events.append(
                        (_t.perf_counter() - self._record_start,
                         ch, midi_note, 0, False))
            return True
        return False

    def start_recording(self):
        """Start recording MIDI events."""
        import time as _t
        self._record_events = []
        self._record_start = _t.perf_counter()
        self._recording = True

    def stop_recording(self):
        """Stop recording."""
        self._recording = False

    def export_recording(self, filename="recording.mid", bpm=None):
        """Export recorded events to a MIDI file.

        Returns a pytheory Score if no filename given.
        """
        if not self._record_events:
            return None

        use_bpm = bpm or (self._bpm if self._bpm > 10 else 120)

        from .rhythm import Score, Duration

        score = Score("4/4", bpm=int(use_bpm))

        # Group events by channel
        by_channel = {}
        for ts, ch, note, vel, is_on in self._record_events:
            if ch not in by_channel:
                by_channel[ch] = []
            by_channel[ch].append((ts, note, vel, is_on))

        # Build parts — use the channel's configured synth as the
        # part instrument so the exported Score sounds like the session
        picks = getattr(self, 'picks', None)
        for ch, events in sorted(by_channel.items()):
            if picks and 1 <= ch <= len(picks):
                inst = picks[ch - 1]
            else:
                inst = "piano"
            part = score.part(f"ch{ch}", instrument=inst)

            # Convert to note-on/off pairs
            active = {}
            notes = []
            for ts, note, vel, is_on in events:
                if is_on:
                    active[note] = (ts, vel)
                elif note in active:
                    start_ts, start_vel = active.pop(note)
                    dur_sec = ts - start_ts
                    dur_beats = dur_sec * use_bpm / 60.0
                    notes.append((start_ts, note, max(0.125, dur_beats), start_vel))

            notes.sort(key=lambda x: x[0])

            beat_pos = 0.0
            for ts, midi_note, dur, vel in notes:
                note_beat = ts * use_bpm / 60.0
                if note_beat > beat_pos:
                    part.rest(note_beat - beat_pos)
                # Convert MIDI note to name
                name = NOTE_NAMES[midi_note % 12]
                octave = midi_note // 12 - 1
                part.add(f"{name}{octave}", dur, velocity=vel)
                beat_pos = note_beat + dur

        if filename:
            score.save_midi(filename)

        return score

    def save_config(self, filename):
        """Save current configuration to JSON."""
        import json
        config = {
            "seed": self.seed if hasattr(self, 'seed') else None,
            "buffer_size": self.buffer_size,
            "drums": getattr(self, '_drum_pattern_name', None),
            "channels": {},
        }
        for ch, channel in self.channels.items():
            config["channels"][str(ch)] = {
                "synth": channel.synth_name,
                "envelope": channel.envelope_name,
                "volume": channel.volume,
                "pan": channel.pan,
                "reverb": channel.reverb,
                "lowpass": channel.lowpass,
                "chorus": channel.chorus,
                "distortion": channel.distortion,
                "is_drums": channel.is_drums,
            }
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)

    def load_config(self, filename):
        """Load configuration from JSON."""
        import json
        with open(filename) as f:
            config = json.load(f)
        for ch_str, ch_cfg in config.get("channels", {}).items():
            ch = int(ch_str)
            self.channel(ch,
                         synth=ch_cfg.get("synth"),
                         envelope=ch_cfg.get("envelope"),
                         drums=ch_cfg.get("is_drums", False),
                         volume=ch_cfg.get("volume", 0.5),
                         pan=ch_cfg.get("pan", 0.0),
                         reverb=ch_cfg.get("reverb", 0),
                         lowpass=ch_cfg.get("lowpass", 0),
                         chorus=ch_cfg.get("chorus", 0),
                         distortion=ch_cfg.get("distortion", 0))
        if config.get("drums"):
            self.drums(config["drums"])

    def stop(self):
        """Stop the engine."""
        self._stop_event.set()
        if self._link is not None:
            self._link.enabled = False
            self._link = None
        if self._stream:
            self._stream.stop()
        if self._midi_in:
            self._midi_in.close_port()
            self._midi_in.delete()
            self._midi_in = None
