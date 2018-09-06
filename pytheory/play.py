from enum import Enum
import numpy
import scipy.signal

import contextlib
with contextlib.redirect_stdout(None):
    import pygame

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
    t = numpy.linspace(0, 1, 500 * 440/hz, endpoint=False)
    wave = scipy.signal.sawtooth(2 * numpy.pi * 5 * t, width=rising_ramp_width)
    wave = numpy.resize(wave, (n_samples,))
    # Sawtooth waves sound very quiet, so multiply peak by 4.
    return (peak * 6 * wave.astype(numpy.int16))


def _play_for(sample_wave, ms):
    """Play the given NumPy array, as a sound, for ms milliseconds."""
    sound = pygame.sndarray.make_sound(sample_wave)
    sound.play(-1)
    pygame.time.delay(ms)
    sound.stop()


class Synth(Enum):
    SINE = sine_wave
    SAW = sawtooth_wave

def play(tone_or_chord, temperament='equal', synth=Synth.SINE, t=1_000):

    pygame.mixer.pre_init(SAMPLE_RATE, -16, 1)
    pygame.mixer.init()

    if isinstance(tone_or_chord, Tone):
        chord = [synth(tone_or_chord.pitch(temperament=temperament, symbolic=True))]
    else:
        chord = [synth(tone.pitch(temperament=temperament, symbolic=True)) for tone in tone_or_chord.tones]

    _play_for(sum(chord), ms=t)

#  69 + 12*np.log2(hz_nonneg/440.)
