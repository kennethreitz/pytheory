from enum import Enum
import numpy
import scipy.signal
import sounddevice as sd

from .tones import Tone

SAMPLE_RATE = 44_100
SAMPLE_PEAK = 4_096


def sine_wave(hz, peak=SAMPLE_PEAK, n_samples=SAMPLE_RATE):
    """Compute N samples of a sine wave with given frequency and peak amplitude.
    Defaults to one second.
    """
    length = SAMPLE_RATE / float(hz)
    omega = numpy.pi * 2 / length
    xvalues = numpy.arange(int(length)) * omega
    onecycle = peak * numpy.sin(xvalues)
    return numpy.resize(onecycle, (n_samples,)).astype(numpy.int16)


def sawtooth_wave(hz, peak=SAMPLE_PEAK, rising_ramp_width=1, n_samples=SAMPLE_RATE):
    """Compute N samples of a sine wave with given frequency and peak amplitude.
    Defaults to one second.
    rising_ramp_width is the percentage of the ramp spend rising:
    .5 is a triangle wave with equal rising and falling times.
    """
    t = numpy.linspace(0, 1, 500 * 440 / hz, endpoint=False)
    wave = scipy.signal.sawtooth(2 * numpy.pi * 5 * t, width=rising_ramp_width)
    wave = numpy.resize(wave, (n_samples,))
    # Sawtooth waves sound very quiet, so multiply peak by 4.
    return peak * 6 * wave.astype(numpy.int16)


def triangle_wave(hz, peak=SAMPLE_PEAK, rising_ramp_width=0.5, n_samples=SAMPLE_RATE):
    """Compute N samples of a triangle wave with given frequency and peak amplitude.
    Defaults to one second.
    rising_ramp_width is the percentage of the ramp spend rising:
    .5 is a triangle wave with equal rising and falling times.
    """
    hz_value = float(hz)
    num_samples = int(500 * 440 / hz_value)
    t = numpy.linspace(0, 1, num_samples, endpoint=False)
    wave = scipy.signal.sawtooth(2 * numpy.pi * 5 * t, width=rising_ramp_width)
    wave = numpy.resize(wave, (n_samples,))
    # Use same amplitude as sawtooth_wave for testing
    return peak * 6 * wave.astype(numpy.int16)


def _play_for(sample_wave, ms):
    """Play the given NumPy array, as a sound, for ms milliseconds."""

    # sounddevice expects float32 samples between -1 and 1
    normalized_wave = sample_wave.astype(numpy.float32) / SAMPLE_PEAK

    # Play the audio and wait
    sd.play(normalized_wave, SAMPLE_RATE)
    sd.wait()


class Synth(Enum):
    SINE = sine_wave
    SAW = sawtooth_wave
    TRIANGLE = triangle_wave


def play(tone_or_chord, temperament="equal", synth=Synth.SINE, t=1_000):
    """Play a tone or chord."""

    if isinstance(tone_or_chord, Tone):
        chord = [synth(tone_or_chord.pitch(temperament=temperament, symbolic=True))]
    else:
        chord = [
            synth(tone.pitch(temperament=temperament, symbolic=True))
            for tone in tone_or_chord.tones
        ]

    _play_for(sum(chord), ms=t)


#  69 + 12*np.log2(hz_nonneg/440.)
