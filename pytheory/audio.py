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


def _chromagram(samples, sample_rate=SAMPLE_RATE, *,
                fmin=55.0, fmax=5000.0):
    """Fold a spectrogram into 12 pitch classes over time.

    Every FFT bin maps to the pitch class of its frequency; summing
    magnitudes per class gives a "chroma" vector per frame — a
    fingerprint of what harmony is sounding, regardless of octave.

    Returns:
        (chroma, frame_times) — chroma is shape (12, n_frames),
        columns normalized to unit sum.
    """
    from scipy.signal import stft

    nperseg = 4096
    hop = 1024
    f, t, Z = stft(samples, fs=sample_rate, nperseg=nperseg,
                   noverlap=nperseg - hop)
    mag = numpy.abs(Z)

    # Map bins to pitch classes (ignore rumble and air)
    usable = (f >= fmin) & (f <= fmax)
    midi = 69 + 12 * numpy.log2(f[usable] / 440.0)
    pcs = numpy.round(midi).astype(int) % 12

    chroma = numpy.zeros((12, mag.shape[1]))
    usable_mag = mag[usable]
    for pc in range(12):
        sel = pcs == pc
        if sel.any():
            chroma[pc] = usable_mag[sel].sum(axis=0)
    totals = chroma.sum(axis=0)
    totals[totals == 0] = 1.0
    return chroma / totals, t


# Chord templates: which pitch classes (relative to the root) sound.
# The root gets extra weight — it's usually doubled and in the bass.
# Each entry is (intervals, prior): four-note chords get a slight
# handicap so a plain triad with a passing melody note doesn't get
# promoted to a 7th.
_CHORD_QUALITIES = {
    "": ((0, 4, 7), 1.0),         # major
    "m": ((0, 3, 7), 1.0),        # minor
    "7": ((0, 4, 7, 10), 0.96),   # dominant 7th
    "maj7": ((0, 4, 7, 11), 0.96),
    "m7": ((0, 3, 7, 10), 0.96),
    "sus2": ((0, 2, 7), 0.94),
    "sus4": ((0, 5, 7), 0.94),
}


def _grid_phase(samples, sample_rate, window_sec):
    """Find where the chord grid should start, in seconds.

    Chord changes land on beats, but the recording rarely starts on
    one. Fold onset energy (spectral flux) onto the window period —
    a circular histogram of "when in the window do onsets happen" —
    and start the grid at the phase where they concentrate.
    """
    from scipy.signal import stft

    hop = 512
    nperseg = 2048
    if len(samples) < nperseg * 2:
        return 0.0
    f, t, Z = stft(samples, fs=sample_rate, nperseg=nperseg,
                   noverlap=nperseg - hop)
    mag = numpy.abs(Z)
    flux = numpy.maximum(numpy.diff(mag, axis=1), 0).sum(axis=0)
    ftimes = t[1:]
    if flux.std() < 1e-9:
        return 0.0
    flux = flux - flux.min()

    nbins = 64
    hist = numpy.zeros(nbins)
    idx = ((ftimes % window_sec) / window_sec * nbins).astype(int) % nbins
    numpy.add.at(hist, idx, flux)
    # Circular smoothing so an onset straddling two bins still wins
    kernel = numpy.array([0.25, 0.5, 1.0, 0.5, 0.25])
    smooth = sum(k * numpy.roll(hist, s)
                 for k, s in zip(kernel, range(-2, 3)))
    return float(smooth.argmax()) / nbins * window_sec


def _bass_is_real(bass_sig, sample_rate, lo, hi, f_bass):
    """Is there actual spectral energy at the detected bass pitch?

    YIN reports the period of the *composite* waveform, so a chord
    with no bass note still yields its missing fundamental (Csus4
    looks like a phantom F2). A real bass note carries energy at its
    own fundamental; a phantom doesn't.
    """
    seg = bass_sig[int(lo * sample_rate):int(hi * sample_rate)]
    if len(seg) < 1024 or f_bass <= 0:
        return False
    spec = numpy.abs(numpy.fft.rfft(seg * numpy.hanning(len(seg)))) ** 2
    freqs = numpy.fft.rfftfreq(len(seg), 1 / sample_rate)
    fund = spec[(freqs > f_bass * 0.94) & (freqs < f_bass * 1.06)].sum()
    low = spec[freqs < 320.0].sum() + 1e-12
    return fund > 0.2 * low


def detect_chords(samples, sample_rate=SAMPLE_RATE, *, bpm=120,
                  beats_per_chord=2.0):
    """Detect a chord progression from audio.

    Folds the harmonic content into pitch classes (a chromagram),
    averages it over chord-sized windows on a beat grid aligned to
    the music's own onsets, and matches each window against
    major/minor/sus triad and 7th-chord templates on all twelve
    roots. When the bass clearly sits on a chord tone other than the
    root, the chord is reported as a slash chord (``"C/E"``).

    Returns:
        List of (start_beat, duration_beats, symbol) tuples, with
        consecutive identical chords merged — e.g.
        ``[(0.0, 8.0, "Am"), (8.0, 4.0, "F")]``.
    """
    samples = numpy.asarray(samples, dtype=numpy.float64)
    if len(samples) < 8192:
        return []
    # Chroma from 130 Hz up — below that, FFT bins are a semitone
    # wide and a loud bass smears into neighboring pitch classes.
    # The bass still votes through its harmonics.
    chroma, times = _chromagram(samples, sample_rate, fmin=130.0)
    if chroma.shape[1] == 0:
        return []
    # Bass pitch track for inversion detection — the chromagram is
    # octave-blind (and FFT bins are semitones wide down low), so
    # "what's in the bass?" gets its own YIN pass on the lowpassed
    # signal, like the bass stem in transcribe().
    from scipy.signal import butter, filtfilt
    bl, al = butter(4, 320, btype='low', fs=sample_rate)
    bass_sig = filtfilt(bl, al, samples)
    btimes, bfreqs, bvoiced = detect_pitch(bass_sig, sample_rate,
                                           fmin=40.0, fmax=300.0)

    # Build the templates once (12 roots × qualities)
    templates = []
    for root in range(12):
        for quality, (intervals, prior) in _CHORD_QUALITIES.items():
            vec = numpy.zeros(12)
            for iv in intervals:
                vec[(root + iv) % 12] = 1.0
            vec[root] = 1.5          # weight the root
            vec /= numpy.linalg.norm(vec)
            templates.append((root, quality,
                              frozenset((root + iv) % 12 for iv in intervals),
                              vec * prior))

    window_sec = beats_per_chord * 60.0 / bpm
    total_sec = times[-1]
    if total_sec < window_sec / 2:
        return []

    # Beat-align the grid: window boundaries snap to the phase where
    # the music's onsets land, instead of marching blindly from t=0.
    offset = _grid_phase(samples, sample_rate, window_sec)
    boundaries = list(numpy.arange(offset, total_sec, window_sec))
    if not boundaries or boundaries[0] > 1e-6:
        # Leading partial window — usually a silent lead-in (the
        # energy gate below skips it) or the tail of chord one
        # (merged below).
        boundaries.insert(0, 0.0)
    boundaries.append(max(total_sec, boundaries[-1] + 1e-6))

    def to_beats(sec):
        # Snap to sixteenths so the score grid stays tidy
        return round(sec * bpm / 60.0 * 4) / 4.0

    peak_rms = numpy.sqrt((samples ** 2).mean()) or 1.0

    raw = []
    for lo, hi in zip(boundaries[:-1], boundaries[1:]):
        cols = (times >= lo) & (times < hi)
        if not cols.any():
            continue
        # Skip near-silent windows (lead-ins, gaps) — any chroma
        # there is just noise.
        seg = samples[int(lo * sample_rate):int(hi * sample_rate)]
        if len(seg) and numpy.sqrt((seg ** 2).mean()) < 0.05 * peak_rms:
            continue
        avg = chroma[:, cols].mean(axis=1)
        norm = numpy.linalg.norm(avg)
        if norm < 1e-9:
            continue
        avg = avg / norm
        scores = [(avg @ vec, root, quality, pcs)
                  for root, quality, pcs, vec in templates]
        score, root, quality, pcs = max(scores)
        symbol = _NOTE_NAMES[root] + quality

        # Inversion: a confident, steady bass note on a chord tone
        # that isn't the root makes it a slash chord.
        bsel = bvoiced & (btimes >= lo) & (btimes < hi)
        n_window = max(1, int(((btimes >= lo) & (btimes < hi)).sum()))
        if bsel.sum() >= 0.4 * n_window:
            bmidi = numpy.round(
                69 + 12 * numpy.log2(bfreqs[bsel] / 440.0)).astype(int)
            bpcs, counts = numpy.unique(bmidi % 12, return_counts=True)
            bass_pc = int(bpcs[counts.argmax()])
            if (counts.max() >= 0.6 * bsel.sum() and bass_pc != root
                    and bass_pc in pcs
                    and _bass_is_real(bass_sig, sample_rate, lo, hi,
                                      float(numpy.median(
                                          bfreqs[bsel][bmidi % 12
                                                       == bass_pc])))):
                symbol += "/" + _NOTE_NAMES[bass_pc]

        start_b, end_b = to_beats(lo), to_beats(hi)
        if end_b > start_b:
            raw.append((start_b, end_b - start_b, symbol))

    # Merge consecutive identical chords
    merged = []
    for start, dur, sym in raw:
        if merged and merged[-1][2] == sym \
                and abs(merged[-1][0] + merged[-1][1] - start) < 1e-6:
            prev = merged.pop()
            merged.append((prev[0], prev[1] + dur, sym))
        else:
            merged.append((start, dur, sym))
    return merged


def detect_drums(samples, sample_rate=SAMPLE_RATE, *, bpm=120,
                 quantize=0.25):
    """Detect drum hits from (ideally percussive) audio.

    Finds onsets in the energy envelope, then classifies each by
    where its energy lives: kicks are bottom-heavy, hats are all
    sizzle, snares are the broadband middle.

    Returns:
        List of (beat_position, sound_name, velocity) tuples, where
        sound_name is ``"kick"``, ``"snare"``, or ``"closed_hat"``.
    """
    hop = 256
    n_frames = (len(samples) - hop) // hop
    if n_frames < 4:
        return []
    frames = samples[:n_frames * hop].reshape(n_frames, hop)
    env = numpy.sqrt((frames ** 2).mean(axis=1))
    peak_env = env.max() or 1.0

    # Onsets: env rises sharply above its local past. Pad with
    # silence so a hit on the very first sample still registers.
    pad = 6
    env_p = numpy.concatenate([numpy.zeros(pad), env])
    onsets = []
    last = -10_000
    for i in range(n_frames):
        recent = env_p[i:i + pad].min()
        if (env[i] > 2.0 * recent + 0.02 * peak_env
                and env[i] > 0.08 * peak_env
                and i - last > int(0.09 * sample_rate / hop)):
            onsets.append(i)
            last = i

    hits = []
    win = int(sample_rate * 0.05)
    for i in onsets:
        start = i * hop
        seg = samples[start:start + win]
        if len(seg) < 64:
            continue
        spec = numpy.abs(numpy.fft.rfft(seg * numpy.hanning(len(seg))))
        freqs = numpy.fft.rfftfreq(len(seg), 1 / sample_rate)
        # Per-band MEAN magnitude (sums would bias toward the high
        # band, which has ~100x more FFT bins than the low band)
        low = spec[freqs < 150].mean()
        mid = spec[(freqs >= 150) & (freqs < 2000)].mean()
        high = spec[freqs >= 5000].mean()
        power = spec ** 2
        cent = (power * freqs).sum() / (power.sum() + 1e-12)
        # Thresholds calibrated against pytheory's own kick/snare/hat
        # synths, alone and in mixtures
        sounds = []
        if low > 5 * (mid + 1e-12):
            sounds.append("kick")
            if high > 0.15 * mid:
                sounds.append("closed_hat")  # hat hiding under the kick
        elif cent > 8800:
            sounds.append("closed_hat")
        else:
            sounds.append("snare")
        beat = start / sample_rate * bpm / 60.0
        if quantize:
            beat = round(beat / quantize) * quantize
        vel = int(numpy.clip(50 + 70 * env[i] / peak_env, 1, 127))
        for sound in sounds:
            hits.append((beat, sound, vel))

    # Dedupe hits quantized onto the same grid slot with the same sound
    seen = set()
    out = []
    for beat, sound, vel in hits:
        if (beat, sound) not in seen:
            seen.add((beat, sound))
            out.append((beat, sound, vel))
    return out


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
        harmonic, percussive = hpss(samples, sample_rate)

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

        # Chord pass: chromagram template matching on the harmonic stem
        chord_track = detect_chords(harmonic, sample_rate, bpm=bpm)
        if chord_track:
            from .chords import Chord
            chords = score.part("chords", synth="rhodes", volume=0.4)
            pos = 0.0
            for start, dur, symbol in chord_track:
                if start - pos > 1e-6:
                    chords.rest(start - pos)
                    pos = start
                chords.add(Chord.from_symbol(symbol), dur)
                pos += dur

        # Drum pass: onset classification on the percussive stem
        drum_hits = detect_drums(percussive, sample_rate, bpm=bpm,
                                 quantize=quantize or 0.25)
        if drum_hits:
            from .rhythm import (Pattern, DrumSound, _Hit)
            sound_map = {"kick": DrumSound.KICK,
                         "snare": DrumSound.SNARE,
                         "closed_hat": DrumSound.CLOSED_HAT}
            hits = [_Hit(sound_map[s], beat, vel)
                    for beat, s, vel in drum_hits]
            total = max(h.position for h in hits) + 1.0
            score.add_pattern(Pattern("transcribed", hits, beats=total),
                              repeats=1)

        # Key detection from everything pitched we heard — full chord
        # tones, not just roots (Am-F-G's roots alone are ambiguous;
        # its tones spell out C major / A minor exactly)
        from .chords import Chord
        from .scales import Key
        pitch_classes = []
        for events in (mel_events, bass_events):
            pitch_classes.extend(_NOTE_NAMES[note % 12]
                                 for _, _, note, _ in events)
        for _, _, symbol in chord_track:
            try:
                pitch_classes.extend(
                    t.name for t in Chord.from_symbol(symbol).tones)
            except ValueError:
                pass
        score.detected_key = (Key.detect(*dict.fromkeys(pitch_classes))
                              if pitch_classes else None)
        return score

    events = _track_events(samples, sample_rate, fmin, fmax)
    part = score.part(part_name, synth=synth)
    _events_to_part(part, events, bpm, quantize)
    return score
