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


def sawtooth_wave(hz, peak=SAMPLE_PEAK, n_samples=SAMPLE_RATE):
    """Compute N samples of a sawtooth wave with given frequency and peak amplitude.
    Defaults to one second.
    """
    length = SAMPLE_RATE / float(hz)
    omega = numpy.pi * 2 / length
    xvalues = numpy.arange(int(length)) * omega
    onecycle = scipy.signal.sawtooth(xvalues, width=1)
    onecycle = (peak * onecycle).astype(numpy.int16)
    return numpy.resize(onecycle, (n_samples,))


def triangle_wave(hz, peak=SAMPLE_PEAK, n_samples=SAMPLE_RATE):
    """Compute N samples of a triangle wave with given frequency and peak amplitude.
    Defaults to one second.
    """
    length = SAMPLE_RATE / float(hz)
    omega = numpy.pi * 2 / length
    xvalues = numpy.arange(int(length)) * omega
    onecycle = scipy.signal.sawtooth(xvalues, width=0.5)
    onecycle = (peak * onecycle).astype(numpy.int16)
    return numpy.resize(onecycle, (n_samples,))


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
        chord = [synth(tone_or_chord.pitch(temperament=temperament))]
    else:
        chord = [
            synth(tone.pitch(temperament=temperament))
            for tone in tone_or_chord.tones
        ]

    _play_for(sum(chord), ms=t)


#  69 + 12*np.log2(hz_nonneg/440.)
