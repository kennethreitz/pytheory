"""Audio import — turn a recording back into a Score.

Hum a melody into your phone, whistle a hook, play a bass line —
then load the WAV and get notes you can edit, harmonize, export to
MIDI, or print as sheet music::

    from pytheory import Score

    score = Score.from_wav("hum.wav")
    print(score.parts["melody"].notes)
    score.save_midi("hum.mid")

Transcription is **monophonic**: one note at a time (voice, whistle,
a single instrument line). Chords and polyphonic recordings are a
much harder problem — run melody and bass as separate takes.

The pitch tracker is the YIN algorithm (de Cheveigné & Kawahara,
2002) — the classic autocorrelation-with-a-twist method that powers
most monophonic tuners — implemented in pure numpy.
"""

import numpy

SAMPLE_RATE = 44_100

_NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
               'F#', 'G', 'G#', 'A', 'A#', 'B']


def load_wav(path):
    """Load a WAV file as mono float64 in [-1, 1].

    Handles 8/16/32-bit PCM and float WAVs; stereo is mixed down.

    Returns:
        (samples, sample_rate) tuple.
    """
    from scipy.io import wavfile
    sample_rate, data = wavfile.read(path)
    data = numpy.asarray(data)
    if data.ndim > 1:
        data = data.mean(axis=1)
    if data.dtype == numpy.int16:
        samples = data / 32768.0
    elif data.dtype == numpy.int32:
        samples = data / 2147483648.0
    elif data.dtype == numpy.uint8:
        samples = (data.astype(numpy.float64) - 128.0) / 128.0
    else:
        samples = data.astype(numpy.float64)
    return samples.astype(numpy.float64), sample_rate


def detect_pitch(samples, sample_rate=SAMPLE_RATE, *,
                 frame_size=2048, hop=512, fmin=50.0, fmax=1500.0,
                 threshold=0.12):
    """Track pitch over time with the YIN algorithm.

    Args:
        samples: Mono float array.
        sample_rate: Sample rate in Hz.
        frame_size: Analysis window (default 2048 ≈ 46ms).
        hop: Samples between frames (default 512 ≈ 12ms).
        fmin/fmax: Pitch search range in Hz.
        threshold: YIN aperiodicity threshold — lower is stricter
            about what counts as a pitched sound.

    Returns:
        (times, freqs, voiced) arrays — one entry per frame. ``freqs``
        is 0 where ``voiced`` is False.
    """
    n = len(samples)
    tau_max = min(int(sample_rate / fmin), frame_size - 2)
    tau_min = max(2, int(sample_rate / fmax))
    n_frames = max(0, (n - frame_size) // hop + 1)

    times = numpy.arange(n_frames) * hop / sample_rate
    freqs = numpy.zeros(n_frames)
    voiced = numpy.zeros(n_frames, dtype=bool)
    if n_frames == 0:
        return times, freqs, voiced

    peak = numpy.abs(samples).max() or 1.0
    fft_size = 1
    while fft_size < 2 * frame_size:
        fft_size *= 2

    for i in range(n_frames):
        frame = samples[i * hop:i * hop + frame_size]

        # Skip silence outright
        rms = numpy.sqrt((frame ** 2).mean())
        if rms < 0.015 * peak:
            continue

        # Difference function via FFT autocorrelation:
        # d(τ) = e[0:W-τ] + e[τ:W] - 2·acf(τ)
        spectrum = numpy.fft.rfft(frame, fft_size)
        acf = numpy.fft.irfft(spectrum * numpy.conj(spectrum))[:tau_max + 1]
        energy = numpy.concatenate(([0.0], numpy.cumsum(frame ** 2)))
        w = frame_size
        taus = numpy.arange(tau_max + 1)
        e_head = energy[w - taus] - energy[0]      # Σ x[0:W-τ]²
        e_tail = energy[w] - energy[taus]          # Σ x[τ:W]²
        d = e_head + e_tail - 2 * acf

        # Cumulative-mean-normalized difference (the YIN twist —
        # stops the trivial d(0)=0 minimum from winning)
        cmndf = numpy.ones(tau_max + 1)
        cum = numpy.cumsum(d[1:])
        cmndf[1:] = d[1:] * taus[1:] / numpy.where(cum > 0, cum, 1e-12)

        # First dip below threshold wins (prefers the true period
        # over its subharmonics); fall back to the global minimum.
        search = cmndf[tau_min:tau_max + 1]
        below = numpy.flatnonzero(search < threshold)
        if len(below):
            tau = tau_min + below[0]
            # Walk to the local minimum of this dip
            while tau + 1 <= tau_max and cmndf[tau + 1] < cmndf[tau]:
                tau += 1
        else:
            tau = tau_min + int(numpy.argmin(search))
            if cmndf[tau] > 0.4:
                continue  # too aperiodic — unvoiced

        # Parabolic interpolation for sub-sample precision
        if 1 <= tau < tau_max:
            a, b, c = cmndf[tau - 1], cmndf[tau], cmndf[tau + 1]
            denom = a - 2 * b + c
            if abs(denom) > 1e-12:
                tau = tau + 0.5 * (a - c) / denom

        freqs[i] = sample_rate / tau
        voiced[i] = True

    return times, freqs, voiced


def _segment_notes(times, freqs, voiced, samples, sample_rate, hop,
                   min_note=0.06, gap_frames=3):
    """Group the frame-wise pitch track into discrete note events.

    Returns a list of (start_sec, dur_sec, midi_note, velocity).
    """
    n_frames = len(times)
    midi = numpy.zeros(n_frames)
    m = voiced & (freqs > 0)
    midi[m] = 69 + 12 * numpy.log2(freqs[m] / 440.0)

    # Median-smooth the pitch track to kill single-frame blips
    if n_frames >= 5:
        from scipy.signal import medfilt
        midi_s = medfilt(midi, 5)
        midi = numpy.where(m, numpy.where(midi_s > 0, midi_s, midi), 0)

    # Frame RMS for velocities and re-articulation onsets
    frame_rms = numpy.zeros(n_frames)
    for i in range(n_frames):
        seg = samples[i * hop:i * hop + hop]
        if len(seg):
            frame_rms[i] = numpy.sqrt((seg ** 2).mean())
    peak_rms = frame_rms.max() or 1.0

    events = []
    cur_frames = []
    cur_start = 0
    silent_run = 0

    def close():
        if not cur_frames:
            return
        seg_midi = numpy.array([midi[j] for j in cur_frames])
        note = int(numpy.round(numpy.median(seg_midi)))
        start = times[cur_start]
        end = times[cur_frames[-1]] + hop / sample_rate
        dur = end - start
        if dur < min_note or not (12 <= note <= 119):
            return
        seg_rms = frame_rms[cur_frames].max()
        vel = int(numpy.clip(40 + 80 * seg_rms / peak_rms, 1, 127))
        events.append((start, dur, note, vel))

    for i in range(n_frames):
        if voiced[i] and midi[i] > 0:
            if not cur_frames:
                cur_frames = [i]
                cur_start = i
            else:
                ref = numpy.median([midi[j] for j in cur_frames])
                re_attack = (
                    len(cur_frames) > 6
                    and frame_rms[i] > 2.5 * frame_rms[max(0, i - 3):i].min()
                    and frame_rms[i] > 0.15 * peak_rms)
                if abs(midi[i] - ref) > 0.6 or re_attack:
                    close()
                    cur_frames = [i]
                    cur_start = i
                else:
                    cur_frames.append(i)
            silent_run = 0
        else:
            if cur_frames:
                silent_run += 1
                if silent_run > gap_frames:
                    close()
                    cur_frames = []
                    silent_run = 0
    close()
    return events


def transcribe(path, *, bpm=120, quantize=None, part_name="melody",
               synth="piano_synth", fmin=50.0, fmax=1500.0):
    """Transcribe a monophonic WAV recording into a Score.

    Args:
        path: WAV file path (or a (samples, sample_rate) tuple).
        bpm: Tempo to interpret the timing against (default 120).
            Durations come out in beats at this tempo.
        quantize: Optional grid in beats (e.g. ``0.25`` snaps note
            starts and lengths to sixteenths). Default: no snapping —
            you get the timing as performed.
        part_name: Name for the created part.
        synth: Synth for playback of the transcription.
        fmin/fmax: Pitch range to search, in Hz. Tighten these for
            better results (e.g. ``fmin=60, fmax=350`` for a bass).

    Returns:
        A :class:`~pytheory.rhythm.Score` with one part holding the
        detected notes, rests, and velocities.
    """
    from .rhythm import Score

    if isinstance(path, tuple):
        samples, sample_rate = path
    else:
        samples, sample_rate = load_wav(path)

    hop = 512
    times, freqs, voiced = detect_pitch(
        samples, sample_rate, hop=hop, fmin=fmin, fmax=fmax)
    events = _segment_notes(times, freqs, voiced, samples, sample_rate, hop)

    score = Score("4/4", bpm=bpm)
    part = score.part(part_name, synth=synth)

    def snap(beats):
        if quantize:
            return max(quantize, round(beats / quantize) * quantize)
        return beats

    pos = 0.0
    for start_s, dur_s, note, vel in events:
        start_b = start_s * bpm / 60.0
        dur_b = dur_s * bpm / 60.0
        if quantize:
            start_b = round(start_b / quantize) * quantize
        gap = start_b - pos
        if gap > 1e-3:
            part.rest(gap)
            pos = start_b
        dur_b = snap(dur_b)
        name = f"{_NOTE_NAMES[note % 12]}{note // 12 - 1}"
        part.add(name, dur_b, velocity=vel)
        pos += dur_b
    return score
