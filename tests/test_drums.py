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


def test_score_total_beats():
    score = Score("4/4", bpm=120)
    score.add(Tone.from_string("C4"), Duration.QUARTER)
    score.add(Tone.from_string("E4"), Duration.HALF)
    score.rest(Duration.QUARTER)
    assert score.total_beats == 4.0


def test_drum_sound_values():
    from pytheory.rhythm import DrumSound
    assert DrumSound.KICK.value == 36
    assert DrumSound.SNARE.value == 38
    assert DrumSound.CLOSED_HAT.value == 42
    assert DrumSound.RIDE.value == 51


def test_pattern_list_presets():
    from pytheory import Pattern
    presets = Pattern.list_presets()
    assert len(presets) >= 40
    assert "rock" in presets
    assert "jazz" in presets
    assert "salsa" in presets
    assert "bossa nova" in presets
    assert "bebop" in presets
    assert "funk" in presets


def test_pattern_preset_rock():
    from pytheory import Pattern
    p = Pattern.preset("rock")
    assert p.name == "rock"
    assert p.beats == 4.0
    assert len(p.hits) > 0


def test_pattern_preset_salsa():
    from pytheory import Pattern
    p = Pattern.preset("salsa")
    assert p.beats == 8.0  # 2-bar clave cycle
    assert len(p.hits) > 20


def test_pattern_preset_invalid():
    from pytheory import Pattern
    with pytest.raises(ValueError, match="Unknown preset"):
        Pattern.preset("nonexistent")


def test_pattern_to_score():
    from pytheory import Pattern
    p = Pattern.preset("rock")
    score = p.to_score(repeats=4, bpm=120)
    assert score.total_beats == 16.0
    assert score.measures == 4.0


def test_pattern_to_score_waltz():
    from pytheory import Pattern
    p = Pattern.preset("waltz")
    score = p.to_score(repeats=4, bpm=180)
    assert score.total_beats == 12.0
    assert score.bpm == 180


def test_pattern_all_presets_valid():
    from pytheory import Pattern
    for name in Pattern.list_presets():
        p = Pattern.preset(name)
        assert p.beats > 0
        assert len(p.hits) > 0
        score = p.to_score(repeats=1, bpm=120)
        assert score.total_beats == p.beats


def test_pattern_repr():
    from pytheory import Pattern
    p = Pattern.preset("funk")
    r = repr(p)
    assert "funk" in r
    assert "4/4" in r


@needs_portaudio
def test_render_drum_hit_all_sounds():
    from pytheory.play import _render_drum_hit
    from pytheory.rhythm import DrumSound
    for sound in DrumSound:
        wave = _render_drum_hit(sound.value, 22050)
        assert len(wave) == 22050
        assert wave.dtype == numpy.float32


@needs_portaudio
def test_render_pattern_rock():
    from pytheory.play import _render_pattern
    from pytheory import Pattern
    p = Pattern.preset("rock")
    buf = _render_pattern(p, bpm=120)
    assert len(buf) > 0
    assert buf.dtype == numpy.float32
    assert numpy.max(numpy.abs(buf)) <= 0.91  # normalized


@needs_portaudio
def test_render_pattern_all_presets():
    from pytheory.play import _render_pattern
    from pytheory import Pattern
    for name in Pattern.list_presets():
        p = Pattern.preset(name)
        buf = _render_pattern(p, bpm=120)
        assert len(buf) > 0, f"Empty buffer for {name}"


@needs_portaudio
def test_render_pattern_different_tempos():
    from pytheory.play import _render_pattern
    from pytheory import Pattern
    p = Pattern.preset("jazz")
    slow = _render_pattern(p, bpm=60)
    fast = _render_pattern(p, bpm=240)
    assert len(slow) > len(fast)  # slower = more samples


def test_render_pattern_bpm_must_be_positive():
    from pytheory.play import _render_pattern
    from pytheory import Pattern
    with pytest.raises(ValueError, match="bpm must be positive"):
        _render_pattern(Pattern.preset("rock"), bpm=0)


def test_part_total_beats_in_score():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    lead.add("C5", Duration.WHOLE).add("E5", Duration.WHOLE)
    assert score.total_beats == 8.0


def test_score_add_pattern():
    from pytheory import Score, Pattern
    score = Score("4/4", bpm=120)
    score.add_pattern(Pattern.preset("rock"), repeats=2)
    assert score._drum_pattern_beats == 8.0
    assert len(score._drum_hits) > 0


def test_score_add_pattern_chaining():
    from pytheory import Score, Pattern
    score = Score("4/4", bpm=120)
    result = score.add_pattern(Pattern.preset("rock"), repeats=1)
    assert result is score


def test_hit_public_export_and_alias():
    from pytheory import Hit, DrumSound
    from pytheory.rhythm import _Hit
    assert Hit is _Hit  # back-compat alias
    h = Hit(DrumSound.KICK, 1.5, velocity=80)
    assert h.sound is DrumSound.KICK
    assert h.position == 1.5
    assert h.velocity == 80


def test_pattern_from_public_hits():
    from pytheory import Pattern, Hit, DrumSound
    beat = Pattern("custom", [Hit(DrumSound.KICK, 0.0),
                              Hit(DrumSound.SNARE, 2.0)])
    assert len(beat.hits) == 2
    assert beat.beats == 4.0


def test_drums_accepts_pattern_object():
    from pytheory import Score, Pattern, Hit, DrumSound
    beat = Pattern("custom", [Hit(DrumSound.KICK, 0.0),
                              Hit(DrumSound.SNARE, 2.0)])
    score = Score("4/4", bpm=120)
    score.drums(beat, repeats=2)
    assert len(score._drum_hits) == 4
    assert score._drum_pattern_beats == 8.0


def test_add_pattern_layer_overlays():
    from pytheory import Score, Pattern
    score = Score("4/4", bpm=120)
    score.add_pattern(Pattern.preset("rock"), repeats=1)  # beats 0..3.5
    score.add_pattern(Pattern.preset("rock"), repeats=1, layer=True)
    # Layered copy overlays from beat 0, so nothing lands past the first bar.
    assert max(h.position for h in score._drum_hits) < 4.0
    # ...and the running playhead is left untouched.
    assert score._drum_pattern_beats == 4.0


def test_drums_layer_keeps_cursor_at_furthest_extent():
    from pytheory import Score
    score = Score("4/4", bpm=120)
    score.drums("rock", repeats=2)            # 8 beats
    score.drums("rock", repeats=1, layer=True)  # overlaid, shorter
    assert score._drum_pattern_beats == 8.0   # unchanged — shorter overlay
    score.drums("rock", repeats=1)            # sequential add resumes after 8
    assert max(h.position for h in score._drum_hits) >= 8.0


def test_fill_presets_exist():
    from pytheory import Pattern
    expected = [
        "rock", "rock crash", "jazz", "jazz brush", "salsa", "samba",
        "funk", "metal", "blast", "buildup", "breakdown",
        "reggae", "afrobeat", "bossa nova", "house", "trap",
        "hip hop", "disco", "cumbia", "highlife", "second line",
    ]
    for name in expected:
        p = Pattern.fill(name)
        assert p is not None


def test_fill_is_pattern():
    from pytheory import Pattern
    p = Pattern.fill("rock")
    assert isinstance(p, Pattern)


def test_fill_beats():
    from pytheory import Pattern
    for name in Pattern.list_fills():
        p = Pattern.fill(name)
        assert p.beats == 4.0, f"Fill {name!r} should be 4 beats, got {p.beats}"


def test_fill_invalid_raises():
    from pytheory import Pattern
    with pytest.raises(ValueError, match="Unknown fill"):
        Pattern.fill("nonexistent_fill_xyz")


def test_score_fill():
    from pytheory import Score
    score = Score("4/4", bpm=120)
    score.fill("rock")
    assert len(score._drum_hits) > 0


def test_drums_with_fill():
    from pytheory import Score
    score = Score("4/4", bpm=120)
    score.drums("rock", repeats=8, fill="rock", fill_every=4)
    # 8 bars total, each 4 beats = 32 beats
    assert score._drum_pattern_beats == 32.0


def test_drums_fill_last_bar_only():
    from pytheory import Score, Pattern
    score = Score("4/4", bpm=120)
    score.drums("rock", repeats=4, fill="rock")
    # 4 bars total, each 4 beats = 16 beats
    assert score._drum_pattern_beats == 16.0
    # The last bar should be a fill (different hit count than groove)
    groove = Pattern.preset("rock")
    fill_pat = Pattern.fill("rock")
    # Build expected: 3 bars groove + 1 bar fill
    expected_hits = 3 * len(groove.hits) + len(fill_pat.hits)
    assert len(score._drum_hits) == expected_hits


def test_fill_all_presets_valid():
    from pytheory import Pattern
    for name in Pattern.list_fills():
        p = Pattern.fill(name)
        assert len(p.hits) > 0, f"Fill {name!r} has no hits"


def test_new_groove_presets():
    from pytheory import Pattern
    new_grooves = [
        "country", "ska", "dub", "jungle", "techno",
        "gospel", "swing", "bolero", "tango", "flamenco",
    ]
    for name in new_grooves:
        p = Pattern.preset(name)
        assert len(p.hits) > 0, f"Groove {name!r} has no hits"


def test_new_fill_presets():
    from pytheory import Pattern
    new_fills = [
        "reggae", "afrobeat", "bossa nova", "house", "trap",
        "hip hop", "disco", "cumbia", "highlife", "second line",
    ]
    for name in new_fills:
        p = Pattern.fill(name)
        assert len(p.hits) > 0, f"Fill {name!r} has no hits"


def test_repl_cmd_drums():
    from pytheory.repl import Session, cmd_drums
    s = Session()
    cmd_drums(s, ["rock"])
    assert s._drum_preset == "rock"
    assert len(s.score._drum_hits) > 0


def test_world_drum_pattern_presets():
    """All world drum patterns should load."""
    from pytheory.rhythm import Pattern
    for name in ["bhangra", "dhol chaal", "qawwali", "dholak folk",
                 "adi talam", "mridangam korvai", "djembe", "kuku", "soli",
                 "double kick", "metal blast", "metal groove", "metal gallop"]:
        p = Pattern.preset(name)
        assert p.beats > 0


def test_cajon_patterns():
    from pytheory.rhythm import Pattern
    for name in ["cajon", "cajon rumba", "cajon folk"]:
        p = Pattern.preset(name)
        assert p.beats > 0


def test_part_hit_adds_note():
    from pytheory.rhythm import DrumSound, _DrumTone
    score = pytheory.Score("4/4", bpm=120)
    p = score.part("kit", synth="sine")
    p.hit(DrumSound.KICK, Duration.QUARTER, velocity=100)
    p.hit(DrumSound.SNARE, Duration.QUARTER, velocity=90, articulation="accent")
    assert len(p.notes) == 2
    assert isinstance(p.notes[0].tone, _DrumTone)
    assert p.notes[0].tone.sound == DrumSound.KICK
    assert p.notes[1].articulation == "accent"


@needs_portaudio
def test_part_hit_renders():
    """Part.hit() drum sounds should render through the note pipeline."""
    from pytheory.rhythm import DrumSound
    from pytheory.play import render_score
    score = pytheory.Score("4/4", bpm=120)
    p = score.part("kit", synth="sine", volume=0.5)
    p.hit(DrumSound.KICK, Duration.QUARTER)
    p.hit(DrumSound.SNARE, Duration.QUARTER)
    p.hit(DrumSound.CLOSED_HAT, Duration.QUARTER)
    p.hit(DrumSound.CRASH, Duration.QUARTER)
    buf = render_score(score)
    assert len(buf) > 0


def test_djembe_patterns_exist():
    from pytheory.rhythm import Pattern
    for name in ["djembe", "kuku", "soli", "dununba", "tiriba",
                 "yankadi", "djansa", "mendiani"]:
        p = Pattern.preset(name)
        assert p.beats > 0
        assert len(p.hits) > 0


def test_djembe_fills_exist():
    from pytheory.rhythm import Pattern
    for name in ["djembe call", "djembe roll", "djembe break"]:
        f = Pattern.fill(name)
        assert f.beats == 4.0
        assert len(f.hits) > 0


def test_cajon_fills_exist():
    from pytheory.rhythm import Pattern
    for name in ["cajon flam", "cajon rumble", "cajon breakdown"]:
        f = Pattern.fill(name)
        assert f.beats == 4.0
        assert len(f.hits) > 0


def test_metal_fills_exist():
    from pytheory.rhythm import Pattern
    for name in ["metal triplet", "metal blast", "metal cascade"]:
        f = Pattern.fill(name)
        assert f.beats == 4.0
        assert len(f.hits) > 0


def test_hpss_separates_drums_from_notes():
    from pytheory.audio import hpss
    from pytheory.play import organ_wave, _synth_snare, SAMPLE_PEAK
    sr = 44100
    tone = organ_wave(220, n_samples=sr * 2).astype(numpy.float64) / SAMPLE_PEAK

    def rms(x):
        return numpy.sqrt((x ** 2).mean())

    h, p = hpss(tone, sr)
    assert rms(h) > 3 * rms(p)         # held note → harmonic

    drums = numpy.zeros(sr * 2)
    for i in range(8):
        hit = _synth_snare(sr // 8)
        start = i * sr // 4
        drums[start:start + len(hit)] += hit
    h, p = hpss(drums, sr)
    assert rms(p) > rms(h)             # snare hits → percussive


def test_detect_drums_classifies_kick_snare_hat():
    from pytheory.audio import detect_drums
    from pytheory.play import _synth_kick, _synth_snare, _synth_hat_closed
    sr = 44100
    sig = numpy.zeros(sr * 2)
    layout = [(0.0, _synth_kick, "kick"), (0.5, _synth_snare, "snare"),
              (1.0, _synth_hat_closed, "closed_hat"),
              (1.5, _synth_kick, "kick")]
    for t0, fn, _ in layout:
        hit = fn(sr // 4)
        start = int(t0 * sr)
        sig[start:start + len(hit)] += hit
    hits = detect_drums(sig / (numpy.abs(sig).max() or 1), sr,
                        bpm=120, quantize=0.5)
    found = {(b, s) for b, s, _ in hits}
    for t0, _, name in layout:
        assert (t0 * 2, name) in found  # 120bpm → beat = 2*seconds
