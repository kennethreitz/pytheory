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
    """Load an audio file as mono float64 in [-1, 1].

    WAV files (8/16/32-bit PCM and float) are read directly; stereo is
    mixed down. Anything else — .m4a voice memos, .mp3, .aiff — is
    converted on the fly through ``afconvert`` (built into macOS) or
    ``ffmpeg``, whichever is on your PATH.

    Returns:
        (samples, sample_rate) tuple.
    """
    if not str(path).lower().endswith(".wav"):
        return _load_via_converter(path)
    return _read_wav(path)


def _read_wav(path):
    import warnings
    from scipy.io import wavfile
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # metadata chunks are fine to skip
        sample_rate, data = wavfile.read(path)
    data = numpy.asarray(data)
    # Normalize by the source dtype BEFORE the stereo mixdown —
    # averaging channels converts to float64 and would hide the dtype.
    if data.dtype == numpy.int16:
        data = data / 32768.0
    elif data.dtype == numpy.int32:
        data = data / 2147483648.0
    elif data.dtype == numpy.uint8:
        data = (data.astype(numpy.float64) - 128.0) / 128.0
    else:
        data = data.astype(numpy.float64)
    if data.ndim > 1:
        data = data.mean(axis=1)
    return data.astype(numpy.float64), sample_rate


def _load_via_converter(path):
    """Convert a non-WAV file to WAV via afconvert or ffmpeg, then read it."""
    import os
    import shutil
    import subprocess
    import tempfile

    fd, tmp = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        if shutil.which("afconvert"):
            subprocess.run(
                ["afconvert", "-f", "WAVE", "-d", "LEI16@44100",
                 str(path), tmp],
                check=True, capture_output=True)
        elif shutil.which("ffmpeg"):
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(path), "-ar", "44100", tmp],
                check=True, capture_output=True)
        else:
            raise RuntimeError(
                f"Can't read {path!r}: converting non-WAV audio needs "
                f"afconvert (built into macOS) or ffmpeg on your PATH.")
        return _read_wav(tmp)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def hpss(samples, sample_rate=SAMPLE_RATE, *, kernel=31):
    """Harmonic-percussive source separation.

    Drums and notes look completely different on a spectrogram:
    a held note is a horizontal line (steady frequency over time), a
    drum hit is a vertical line (all frequencies at one instant).
    Median-filter the spectrogram along time and you keep the
    horizontals; along frequency and you keep the verticals. Soft
    masks built from the two estimates split the signal.

    Returns:
        (harmonic, percussive) sample arrays, same length as input.
    """
    from scipy.signal import stft, istft
    from scipy.ndimage import median_filter

    nperseg = 2048
    f, t, Z = stft(samples, fs=sample_rate, nperseg=nperseg,
                   noverlap=nperseg * 3 // 4)
    mag = numpy.abs(Z)
    harm = median_filter(mag, size=(1, kernel))
    perc = median_filter(mag, size=(kernel, 1))
    # Soft Wiener-style masks
    h2, p2 = harm ** 2, perc ** 2
    total = h2 + p2 + 1e-12
    _, harmonic = istft(Z * (h2 / total), fs=sample_rate,
                        nperseg=nperseg, noverlap=nperseg * 3 // 4)
    _, percussive = istft(Z * (p2 / total), fs=sample_rate,
                          nperseg=nperseg, noverlap=nperseg * 3 // 4)
    n = len(samples)
    return harmonic[:n], percussive[:n]


def estimate_tempo(samples, sample_rate=SAMPLE_RATE, *,
                   bpm_min=60, bpm_max=200):
    """Estimate tempo from the onset pattern.

    Builds an onset-strength envelope (spectral flux — how much new
    energy appears frame to frame), autocorrelates it, and finds the
    beat period that explains the recording best, gently preferring
    tempos near 120.

    Returns:
        Estimated BPM as an int, or None if the recording doesn't
        have a confident pulse (e.g. rubato humming).
    """
    from scipy.signal import stft

    hop = 512
    nperseg = 2048
    if len(samples) < sample_rate * 2:
        return None
    f, t, Z = stft(samples, fs=sample_rate, nperseg=nperseg,
                   noverlap=nperseg - hop)
    mag = numpy.abs(Z)
    flux = numpy.maximum(numpy.diff(mag, axis=1), 0).sum(axis=0)
    if flux.std() < 1e-9:
        return None
    flux = (flux - flux.mean()) / flux.std()

    frame_rate = sample_rate / hop
    lag_min = int(frame_rate * 60.0 / bpm_max)
    lag_max = min(int(frame_rate * 60.0 / bpm_min), len(flux) - 1)
    if lag_max <= lag_min:
        return None

    ac = numpy.correlate(flux, flux, mode='full')[len(flux) - 1:]
    ac = ac / (ac[0] or 1.0)
    lags = numpy.arange(lag_min, lag_max + 1)
    bpms = 60.0 * frame_rate / lags
    # Log-gaussian prior centered at 120 BPM — resolves the
    # half/double-time ambiguity the way a human tapping along would
    prior = numpy.exp(-0.5 * (numpy.log2(bpms / 120.0) / 0.9) ** 2)
    scores = ac[lags] * prior
    best = int(numpy.argmax(scores))
    if ac[lags][best] < 0.1:
        return None  # no confident pulse
    return int(round(bpms[best]))


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


def _events_to_part(part, events, bpm, quantize):
    """Write (start, dur, midi, vel) events into a Part as notes/rests."""
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


def _track_events(samples, sample_rate, fmin, fmax):
    """Pitch-track a signal and return segmented note events."""
    hop = 512
    times, freqs, voiced = detect_pitch(
        samples, sample_rate, hop=hop, fmin=fmin, fmax=fmax)
    return _segment_notes(times, freqs, voiced, samples, sample_rate, hop)


def transcribe(path, *, bpm=None, quantize=None, split=False,
               part_name="melody", synth="piano_synth",
               fmin=50.0, fmax=1500.0):
    """Transcribe an audio recording into a Score.

    Args:
        path: Audio file path — WAV directly, anything else (.m4a,
            .mp3) via afconvert/ffmpeg. Or a (samples, sample_rate)
            tuple.
        bpm: Tempo to interpret the timing against. Default ``None``
            estimates it from the recording's onset pattern, falling
            back to 120 when there's no confident pulse (rubato
            humming). Pass a number to pin it.
        quantize: Optional grid in beats (e.g. ``0.25`` snaps note
            starts and lengths to sixteenths). Default: no snapping —
            you get the timing as performed.
        split: If True, run harmonic-percussive separation first and
            transcribe **two** parts from the harmonic signal — a
            ``"bass"`` part (40-200 Hz) and a ``"melody"`` part
            (200 Hz up, with the bass filtered out). Use this on full
            mixes; expect the bassline to come out well and the
            melody to come out only as well as it dominates the mix.
        part_name: Name for the created part (non-split mode).
        synth: Synth for playback of the transcription.
        fmin/fmax: Pitch range to search, in Hz (non-split mode).
            Tighten these for better results (e.g. ``fmin=60,
            fmax=350`` for a bass).

    Returns:
        A :class:`~pytheory.rhythm.Score` holding the detected notes,
        rests, and velocities.
    """
    from .rhythm import Score

    if isinstance(path, tuple):
        samples, sample_rate = path
    else:
        samples, sample_rate = load_wav(path)

    if bpm is None:
        bpm = estimate_tempo(samples, sample_rate) or 120

    score = Score("4/4", bpm=int(bpm))

    if split:
        from scipy.signal import butter, filtfilt
        harmonic, _ = hpss(samples, sample_rate)

        # Bass pass: lowpassed harmonic signal, bass-register search
        bl, al = butter(4, 300, btype='low', fs=sample_rate)
        bass_sig = filtfilt(bl, al, harmonic)
        bass_events = _track_events(bass_sig, sample_rate, 40.0, 200.0)

        # Melody pass: bass filtered out, mid/high-register search
        bh, ah = butter(4, 250, btype='high', fs=sample_rate)
        mel_sig = filtfilt(bh, ah, harmonic)
        mel_events = _track_events(mel_sig, sample_rate, 200.0, 1500.0)

        melody = score.part("melody", synth=synth)
        _events_to_part(melody, mel_events, bpm, quantize)
        bass = score.part("bass", synth="bass_guitar")
        _events_to_part(bass, bass_events, bpm, quantize)
        return score

    events = _track_events(samples, sample_rate, fmin, fmax)
    part = score.part(part_name, synth=synth)
    _events_to_part(part, events, bpm, quantize)
    return score
