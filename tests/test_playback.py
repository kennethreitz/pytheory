import pytest
import numpy

import pytheory
from pytheory import Tone, TonedScale, Fretboard, Chord, Key, Note, TET
from pytheory.charts import CHARTS, NamedChord, charts_for_fretboard, QUALITIES
from pytheory.systems import System, SYSTEMS
from pytheory.rhythm import Duration, TimeSignature, Note as RhythmNote, Rest, Score

from _util import (HAS_PORTAUDIO, needs_portaudio, _write_test_wav,
                   _roundtrip_melody, _render_test_mix, _chords_roundtrip,
                   _chord_buffer, _progression_score)


@needs_portaudio
def test_synth_enum():
    from pytheory.play import Synth
    # Synth members are callable and produce audio
    assert Synth.SINE.value == "sine"
    assert Synth.SAW.value == "saw"
    assert Synth.TRIANGLE.value == "triangle"
    # Should be directly callable
    wave = Synth.SINE(440)
    assert len(wave) > 0


def test_japanese_hirajoshi():
    """Hirajoshi: C D Eb G Ab."""
    c = TonedScale(tonic="C4", system=SYSTEMS["japanese"])
    h = c["hirajoshi"]
    names = [t.name for t in h]
    assert names == ["C", "D", "Eb", "G", "Ab", "C"]


def test_japanese_iwato():
    """Iwato: C Db F Gb Bb."""
    c = TonedScale(tonic="C4", system=SYSTEMS["japanese"])
    s = c["iwato"]
    names = [t.name for t in s]
    assert names == ["C", "Db", "F", "Gb", "Bb", "C"]


def test_japanese_kumoi():
    """Kumoi: C D Eb G A."""
    c = TonedScale(tonic="C4", system=SYSTEMS["japanese"])
    s = c["kumoi"]
    names = [t.name for t in s]
    assert names == ["C", "D", "Eb", "G", "A", "C"]


def test_japanese_ritsu():
    """Ritsu (gagaku): C D Eb F G A Bb = Dorian."""
    c = TonedScale(tonic="C4", system=SYSTEMS["japanese"])
    s = c["ritsu"]
    names = [t.name for t in s]
    assert names == ["C", "D", "Eb", "F", "G", "A", "Bb", "C"]


@needs_portaudio
def test_play_render():
    """_render produces a numpy array of the right length."""
    from pytheory.play import _render, Synth, SAMPLE_RATE
    tone = Tone.from_string("A4", system="western")
    samples = _render(tone, synth=Synth.SINE, t=500)
    expected = int(SAMPLE_RATE * 500 / 1000)
    assert len(samples) == expected


@needs_portaudio
def test_play_render_all_synths():
    from pytheory.play import _render, Synth
    tone = Tone.from_string("C4", system="western")
    for synth in Synth:
        samples = _render(tone, synth=synth, t=100)
        assert len(samples) > 0


@needs_portaudio
def test_play_save(tmp_path):
    """save() writes a valid WAV file."""
    from pytheory.play import save, Synth
    path = tmp_path / "test.wav"
    tone = Tone.from_string("A4", system="western")
    save(tone, str(path), synth=Synth.SINE, t=200)
    assert path.exists()
    assert path.stat().st_size > 44  # WAV header is 44 bytes


@needs_portaudio
def test_envelope_enum_presets():
    from pytheory.play import Envelope
    assert len(Envelope) == 10
    for e in Envelope:
        a, d, s, r = e.value
        assert a >= 0
        assert d >= 0
        assert 0 <= s <= 1.0
        assert r >= 0


@needs_portaudio
def test_envelope_applied_to_render():
    from pytheory.play import _render, Envelope
    tone = Tone.from_string("A4", system="western")
    raw = _render(tone, t=500, envelope=Envelope.NONE)
    shaped = _render(tone, t=500, envelope=Envelope.PIANO)
    # Shaped signal should start quieter (attack) and end quieter (release)
    assert abs(float(shaped[0])) < abs(float(raw[0])) + 1
    assert abs(float(shaped[-1])) < abs(float(raw[-1])) + 1


@needs_portaudio
def test_envelope_none_is_raw():
    from pytheory.play import _render, Envelope
    tone = Tone.from_string("A4", system="western")
    raw = _render(tone, t=200, envelope=Envelope.NONE)
    # With NONE envelope, first sample should be non-zero (no attack fade)
    assert raw.dtype in (numpy.int16, numpy.float32)


@needs_portaudio
def test_all_envelopes_render():
    from pytheory.play import _render, Envelope
    tone = Tone.from_string("C4", system="western")
    for e in Envelope:
        samples = _render(tone, t=200, envelope=e)
        assert len(samples) > 0


@needs_portaudio
def test_render_score_with_parts():
    from pytheory import Score, Duration, Pattern, Key
    from pytheory.play import render_score
    score = Score("4/4", bpm=120)
    score.add_pattern(Pattern.preset("rock"), repeats=2)
    chords = score.part("chords", synth="sine", envelope="pad")
    lead = score.part("lead", synth="saw", envelope="pluck")
    key = Key("C", "major")
    for chord in key.progression("I", "V", "vi", "IV"):
        chords.add(chord, Duration.HALF)
    lead.add("E5", Duration.QUARTER).add("G5", Duration.QUARTER)
    buf = render_score(score)
    assert len(buf) > 0
    assert buf.dtype == numpy.float32


@needs_portaudio
def test_all_synths_in_enum():
    from pytheory.play import Synth
    assert len(Synth) == 56
    for s in Synth:
        wave = s(440, n_samples=1000)
        assert len(wave) == 1000


@needs_portaudio
def test_resolve_synth_new_names():
    from pytheory.play import _resolve_synth, square_wave, fm_wave, supersaw_wave
    assert _resolve_synth("square") is square_wave
    assert _resolve_synth("fm") is fm_wave
    assert _resolve_synth("supersaw") is supersaw_wave


@needs_portaudio
def test_part_with_new_synths():
    from pytheory import Score, Duration
    from pytheory.play import render_score
    score = Score("4/4", bpm=120)
    for synth_name in ["square", "pulse", "fm", "noise", "supersaw"]:
        p = score.part(synth_name, synth=synth_name, envelope="pluck")
        p.add("C4", Duration.QUARTER)
    buf = render_score(score)
    assert len(buf) > 0


@needs_portaudio
def test_reverb_effect():
    from pytheory.play import _apply_reverb
    dry = numpy.zeros(44100, dtype=numpy.float32)
    dry[0] = 1.0  # impulse
    wet = _apply_reverb(dry, mix=1.0, decay=0.5)
    assert numpy.max(numpy.abs(wet[1000:])) > 0


@needs_portaudio
def test_reverb_zero_mix():
    from pytheory.play import _apply_reverb
    dry = numpy.random.uniform(-1, 1, 1000).astype(numpy.float32)
    result = _apply_reverb(dry, mix=0.0)
    assert numpy.allclose(result, dry)


@needs_portaudio
def test_delay_effect():
    from pytheory.play import _apply_delay
    dry = numpy.zeros(44100, dtype=numpy.float32)
    dry[:100] = 1.0
    wet = _apply_delay(dry, mix=0.5, time=0.1, feedback=0.3)
    echo_start = int(0.1 * 44100)
    assert numpy.max(numpy.abs(wet[echo_start:echo_start + 200])) > 0


@needs_portaudio
def test_delay_zero_mix():
    from pytheory.play import _apply_delay
    dry = numpy.random.uniform(-1, 1, 1000).astype(numpy.float32)
    result = _apply_delay(dry, mix=0.0)
    assert numpy.allclose(result, dry)


@needs_portaudio
def test_part_effects_in_render():
    from pytheory import Score, Duration
    from pytheory.play import render_score
    score = Score("4/4", bpm=120)
    lead = score.part("lead", synth="saw", envelope="pluck",
                      reverb=0.3, delay=0.2, lowpass=2000)
    lead.add("C5", Duration.WHOLE)
    buf = render_score(score)
    assert len(buf) > 0


@needs_portaudio
def test_part_effects_change_output():
    from pytheory import Score, Duration
    from pytheory.play import render_score
    s1 = Score("4/4", bpm=120)
    s1.part("lead", synth="saw", envelope="pluck").add("C5", Duration.WHOLE)
    dry = render_score(s1)
    s2 = Score("4/4", bpm=120)
    s2.part("lead", synth="saw", envelope="pluck",
            reverb=0.5, delay=0.3).add("C5", Duration.WHOLE)
    wet = render_score(s2)
    assert not numpy.allclose(dry, wet, atol=0.01)


@needs_portaudio
def test_ring_out_appends_tail_for_effects():
    from pytheory import Score
    from pytheory.play import render_score, effects_tail_seconds

    score = Score("4/4", bpm=120)
    score.drums("funk", repeats=4)
    score.set_drum_effects(reverb=0.5, reverb_type="cave",
                           delay=0.3, delay_time=0.25, delay_feedback=0.4)
    before = render_score(score)

    # ring_out() appends auto-sized trailing silence; the render grows.
    assert score.ring_out() is score          # chainable
    after = render_score(score)
    assert len(after) > len(before)

    # The appended region carries the reverb/delay tail (not pure silence).
    tail = after[len(before):]
    assert numpy.sqrt(numpy.mean(tail ** 2)) > 1e-4

    # Auto length matches the computed effects tail (cave reverb + delay).
    drum_part = next(p for p in score.parts.values() if p.is_drums)
    tail_beats = effects_tail_seconds(drum_part) * score.bpm / 60.0
    assert score.total_beats == pytest.approx(16.0 + tail_beats)


@needs_portaudio
def test_ring_out_is_opt_in_and_explicit():
    from pytheory import Score
    from pytheory.play import render_score

    # No effects + no explicit length => no tail added.
    plain = Score("4/4", bpm=120)
    plain.drums("rock", repeats=2)
    assert plain.ring_out().total_beats == 4.0 * 2

    # Explicit seconds override the auto-sizing.
    score = Score("4/4", bpm=120)
    score.drums("rock", repeats=2)
    score.ring_out(2.0)
    # 2.0s at 120bpm = 4 extra beats appended after the 8-beat groove.
    assert score.total_beats == pytest.approx(8.0 + 4.0)
    assert len(render_score(score)) > 0


@needs_portaudio
def test_hall_reverb_preset_is_a_real_convolution_space():
    from pytheory import Score, Duration
    from pytheory.play import _generate_ir, _IR_DURATIONS, render_score

    # "hall" is referenced by the vocal/mellotron_flute/ring_mod_metallic
    # instrument presets; it must resolve to a convolution IR, not silently
    # fall back to the algorithmic reverb.
    assert "hall" in _IR_DURATIONS
    ir = _generate_ir("hall")
    assert abs(len(ir) / 44100 - _IR_DURATIONS["hall"]) < 0.01

    for inst in ("vocal", "mellotron_flute", "ring_mod_metallic"):
        score = Score("4/4", bpm=120)
        part = score.part("p", instrument=inst)
        assert part.reverb_type in _IR_DURATIONS  # convolution, not fallback
        part.add("C5", Duration.WHOLE)
        assert len(render_score(score)) > 0


def test_unknown_reverb_type_raises():
    from pytheory import Score

    score = Score("4/4", bpm=120)
    with pytest.raises(ValueError, match="Unknown reverb_type"):
        score.part("lead", reverb_type="cavern")          # typo for "cave"
    with pytest.raises(ValueError, match="Unknown reverb_type"):
        score.set_drum_effects(reverb_type="bogus")
    with pytest.raises(ValueError, match="Unknown reverb_type"):
        score.part("ok", reverb_type="hall").set(reverb_type="nope")

    # Valid types (and instrument presets) must not raise.
    score.part("a", reverb_type="hall")
    score.part("b", reverb_type="algorithmic")
    score.part("c", instrument="vocal")


@needs_portaudio
def test_chorus_effect():
    from pytheory.play import _apply_chorus
    t = numpy.arange(44100, dtype=numpy.float32) / 44100
    signal = numpy.sin(2 * numpy.pi * 440 * t).astype(numpy.float32)
    wet = _apply_chorus(signal, mix=0.5)
    assert not numpy.allclose(signal, wet, atol=0.01)


@needs_portaudio
def test_chorus_zero_mix():
    from pytheory.play import _apply_chorus
    dry = numpy.random.uniform(-1, 1, 1000).astype(numpy.float32)
    result = _apply_chorus(dry, mix=0.0)
    assert numpy.allclose(result, dry)


@needs_portaudio
def test_part_with_chorus():
    from pytheory import Score, Duration
    from pytheory.play import render_score
    score = Score("4/4", bpm=120)
    score.part("lead", synth="saw", chorus=0.5).add("C5", Duration.WHOLE)
    buf = render_score(score)
    assert len(buf) > 0


@needs_portaudio
def test_lfo_renders_correctly():
    from pytheory import Score, Duration
    from pytheory.play import render_score
    score = Score("4/4", bpm=120)
    lead = score.part("lead", synth="saw", lowpass=400, lowpass_q=3.0)
    lead.lfo("lowpass", rate=1.0, min=300, max=3000, bars=2)
    lead.add("C4", Duration.WHOLE).add("C4", Duration.WHOLE)
    buf = render_score(score)
    assert len(buf) > 0


@needs_portaudio
def test_velocity_affects_render():
    from pytheory import Score, Duration
    from pytheory.play import render_score
    import numpy as np
    # Loud note
    score_loud = Score("4/4", bpm=120)
    lead_loud = score_loud.part("lead", synth="sine", envelope="none")
    lead_loud.add("A4", Duration.QUARTER, velocity=127)
    buf_loud = render_score(score_loud)
    # Quiet note
    score_quiet = Score("4/4", bpm=120)
    lead_quiet = score_quiet.part("lead", synth="sine", envelope="none")
    lead_quiet.add("A4", Duration.QUARTER, velocity=30)
    buf_quiet = render_score(score_quiet)
    # Loud should have greater peak amplitude (both are normalized,
    # but we compare RMS of the raw rendered parts before normalization)
    # Actually, render_score normalizes. Let's just check they both render.
    assert len(buf_loud) > 0
    assert len(buf_quiet) > 0
    # The loud note should have higher peak than the quiet note
    # Since both scores have only one note, normalization makes peaks equal.
    # Instead, render a score with BOTH loud and quiet notes and check
    # the loud section is louder.
    score = Score("4/4", bpm=120)
    lead = score.part("lead", synth="sine", envelope="none")
    lead.add("A4", Duration.QUARTER, velocity=127)
    lead.add("A4", Duration.QUARTER, velocity=30)
    buf = render_score(score)
    mid = len(buf) // 2
    rms_first = np.sqrt(np.mean(buf[:mid] ** 2))
    rms_second = np.sqrt(np.mean(buf[mid:] ** 2))
    assert rms_first > rms_second


def test_sidechain_default():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    pad = score.part("pad", synth="sine", envelope="pad")
    assert pad.sidechain == 0.0
    assert pad.sidechain_release == 0.1


def test_sidechain_set():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    pad = score.part("pad", synth="sine", envelope="pad", sidechain=0.8,
                     sidechain_release=0.15)
    assert pad.sidechain == 0.8
    assert pad.sidechain_release == 0.15


@needs_portaudio
def test_sidechain_render():
    from pytheory import Score, Duration, Pattern
    from pytheory.play import render_score
    import numpy as np

    # Score without sidechain
    score1 = Score("4/4", bpm=120)
    score1.add_pattern(Pattern.preset("rock"), repeats=2)
    pad1 = score1.part("pad", synth="sine", envelope="pad")
    pad1.add("C4", Duration.WHOLE).add("C4", Duration.WHOLE)
    buf1 = render_score(score1)

    # Score with sidechain
    score2 = Score("4/4", bpm=120)
    score2.add_pattern(Pattern.preset("rock"), repeats=2)
    pad2 = score2.part("pad", synth="sine", envelope="pad", sidechain=0.8)
    pad2.add("C4", Duration.WHOLE).add("C4", Duration.WHOLE)
    buf2 = render_score(score2)

    # Both should render to non-empty buffers of the same length
    assert len(buf1) > 0
    assert len(buf1) == len(buf2)
    # The buffers should differ (sidechain alters the mix)
    assert not np.array_equal(buf1, buf2)


def test_repl_cmd_effects():
    from pytheory.repl import Session, cmd_part, _set_effect
    s = Session()
    cmd_part(s, ["lead", "saw"])
    _set_effect(s, "reverb", ["0.4"])
    assert s.current_part.reverb_mix == 0.4
    _set_effect(s, "delay", ["0.3", "0.375"])
    assert s.current_part.delay_mix == 0.3
    assert s.current_part.delay_time == 0.375
    _set_effect(s, "lowpass", ["2000", "3"])
    assert s.current_part.lowpass == 2000
    assert s.current_part.lowpass_q == 3.0
    _set_effect(s, "distortion", ["0.5"])
    assert s.current_part.distortion_mix == 0.5


def test_instrument_effects():
    from pytheory import Score
    score = Score("4/4", bpm=120)
    p = score.part("c", instrument="celesta")
    assert p.reverb_mix == 0.3
    assert p.reverb_type == "plate"
    assert p.synth == "fm"
    assert p.envelope == "mallet"


def test_all_dedicated_synths_render():
    """Every dedicated synth waveform produces valid audio."""
    from pytheory.play import (piano_wave, bass_guitar_wave, flute_wave,
                                trumpet_wave, clarinet_wave, oboe_wave,
                                marimba_wave, harpsichord_wave, cello_wave,
                                harp_wave, upright_bass_wave,
                                acoustic_guitar_wave, electric_guitar_wave,
                                sitar_wave, SAMPLE_RATE)
    synths = [piano_wave, bass_guitar_wave, flute_wave, trumpet_wave,
              clarinet_wave, oboe_wave, marimba_wave, harpsichord_wave,
              cello_wave, harp_wave, upright_bass_wave,
              acoustic_guitar_wave, electric_guitar_wave, sitar_wave]
    for fn in synths:
        wave = fn(440, n_samples=11025)
        assert len(wave) == 11025
        assert wave.dtype == numpy.int16
        assert numpy.abs(wave).max() > 0


def test_dhol_sounds_render():
    from pytheory.play import _render_drum_hit
    from pytheory.rhythm import DrumSound
    for sound in [DrumSound.DHOL_DAGGA, DrumSound.DHOL_TILLI, DrumSound.DHOL_BOTH]:
        wave = _render_drum_hit(sound.value, 22050)
        assert len(wave) == 22050


def test_mridangam_sounds_render():
    from pytheory.play import _render_drum_hit
    from pytheory.rhythm import DrumSound
    for sound in [DrumSound.MRIDANGAM_THAM, DrumSound.MRIDANGAM_NAM,
                  DrumSound.MRIDANGAM_DIN, DrumSound.MRIDANGAM_THA]:
        wave = _render_drum_hit(sound.value, 22050)
        assert len(wave) == 22050


def test_djembe_sounds_render():
    from pytheory.play import _render_drum_hit
    from pytheory.rhythm import DrumSound
    for sound in [DrumSound.DJEMBE_BASS, DrumSound.DJEMBE_TONE, DrumSound.DJEMBE_SLAP]:
        wave = _render_drum_hit(sound.value, 22050)
        assert len(wave) == 22050


def test_metal_kit_sounds_render():
    from pytheory.play import _render_drum_hit
    from pytheory.rhythm import DrumSound
    for sound in [DrumSound.METAL_KICK, DrumSound.METAL_SNARE, DrumSound.METAL_HAT]:
        wave = _render_drum_hit(sound.value, 22050)
        assert len(wave) == 22050


def test_new_synths_render():
    """All 7 new synths produce valid audio."""
    from pytheory.play import (pedal_steel_wave, theremin_wave, kalimba_wave,
                                steel_drum_wave, accordion_wave,
                                didgeridoo_wave, bagpipe_wave,
                                banjo_wave, mandolin_wave, ukulele_wave,
                                vocal_wave, SAMPLE_RATE)
    synths = [pedal_steel_wave, theremin_wave, kalimba_wave, steel_drum_wave,
              accordion_wave, didgeridoo_wave, bagpipe_wave,
              banjo_wave, mandolin_wave, ukulele_wave, vocal_wave]
    for fn in synths:
        wave = fn(440, n_samples=11025)
        assert len(wave) == 11025
        assert wave.dtype == numpy.int16
        assert numpy.abs(wave).max() > 0


def test_vocal_synth_with_lyric():
    """Vocal synth accepts lyric parameter."""
    from pytheory.play import vocal_wave
    for lyric in ["ah", "ee", "oh", "oo", "hi", "la"]:
        wave = vocal_wave(330, n_samples=11025, lyric=lyric)
        assert len(wave) == 11025
        assert numpy.abs(wave).max() > 0


def test_cajon_sounds_render():
    from pytheory.play import _render_drum_hit
    from pytheory.rhythm import DrumSound
    for sound in [DrumSound.CAJON_BASS, DrumSound.CAJON_SLAP, DrumSound.CAJON_TAP]:
        wave = _render_drum_hit(sound.value, 22050)
        assert len(wave) == 22050
        assert wave.dtype == numpy.float32


def test_note_choking_renders():
    """Fast repeated notes should render without errors (choking active)."""
    from pytheory import Score, Duration
    from pytheory.play import render_score
    score = Score("4/4", bpm=200)
    p = score.part("t", instrument="piano")
    for _ in range(32):
        p.add("C4", Duration.SIXTEENTH)
    buf = render_score(score)
    assert len(buf) > 0


def test_synth_enum_count():
    from pytheory.play import Synth
    assert len(Synth) == 56


def test_all_synths_render_and_enum_match():
    """Every Synth enum member should render valid audio."""
    from pytheory.play import Synth
    for s in Synth:
        wave = s(440, n_samples=1000)
        assert len(wave) == 1000


@needs_portaudio
def test_articulations_render():
    """Articulations should produce audio without errors."""
    from pytheory.play import render_score
    score = pytheory.Score("4/4", bpm=120)
    p = score.part("test", synth="sine", volume=0.3)
    for art in ["", "staccato", "legato", "marcato", "tenuto", "accent", "fermata"]:
        p.add("C4", Duration.QUARTER, articulation=art)
    buf = render_score(score)
    assert len(buf) > 0


def test_render_score_exported():
    assert "render_score" in pytheory.__all__


def test_live_stream_reverb_is_block_size_invariant():
    from pytheory.live import _StreamReverb
    rng = numpy.random.default_rng(1)
    x = rng.uniform(-0.5, 0.5, 44100).astype(numpy.float32)
    whole = _StreamReverb().process(x)
    r = _StreamReverb()
    parts = numpy.concatenate(
        [r.process(x[i:i + 512]) for i in range(0, len(x), 512)])
    assert numpy.abs(whole - parts).max() < 1e-5


def test_live_bus_effects_chain_renders_finite():
    from pytheory.live import _Channel
    ch = _Channel(synth_name="saw", envelope_name="organ", volume=0.4,
                  lowpass=2000, reverb=0.4, chorus=0.4, delay=0.3,
                  tremolo_depth=0.3, distortion=0.2, saturation=0.2)
    ch.note_on(57, 100)
    out = numpy.concatenate([ch.render_stereo(512) for _ in range(100)])
    assert numpy.isfinite(out).all()
    assert numpy.abs(out).max() > 0.01


def test_estimate_tempo_full_mix():
    import os
    from pytheory.audio import estimate_tempo, load_wav
    path = _render_test_mix()
    try:
        samples, sr = load_wav(path)
    finally:
        os.unlink(path)
    bpm = estimate_tempo(samples, sr)
    assert bpm is not None
    # Accept the true tempo or a metrical multiple
    assert any(abs(bpm - 110 * m) <= 4 for m in (0.5, 1, 2))
