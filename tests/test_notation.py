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


def test_to_tab_orientation_agnostic():
    """to_tab output is identical regardless of board orientation."""
    from pytheory import Part
    notes = ["C4", "E4", "G4"]
    p_lo = Part("test"); [p_lo.add(n) for n in notes]
    p_hi = Part("test"); [p_hi.add(n) for n in notes]
    assert p_lo.to_tab(tuning=Fretboard.guitar()) == \
        p_hi.to_tab(tuning=Fretboard.guitar(high_to_low=True))


def test_midi_c4():
    c4 = Tone.from_string("C4", system="western")
    assert c4.midi == 60


def test_midi_a4():
    a4 = Tone.from_string("A4", system="western")
    assert a4.midi == 69


def test_midi_c5():
    c5 = Tone.from_string("C5", system="western")
    assert c5.midi == 72


def test_midi_no_octave():
    c = Tone(name="C")
    assert c.midi is None


def test_midi_chromatic_sequence():
    """MIDI numbers should increment by 1 per semitone."""
    c4 = Tone.from_string("C4", system="western")
    for i in range(12):
        assert (c4 + i).midi == 60 + i


def test_from_midi_c4():
    assert Tone.from_midi(60).name == "C"
    assert Tone.from_midi(60).octave == 4


def test_from_midi_a4():
    assert Tone.from_midi(69).name == "A"
    assert Tone.from_midi(69).octave == 4


def test_tone_from_midi_roundtrip():
    """from_midi(tone.midi) should return the same note."""
    for midi in [48, 60, 69, 72, 84]:
        t = Tone.from_midi(midi)
        assert t.midi == midi


def test_chord_from_midi_message():
    c = Chord.from_midi_message(60, 64, 67)
    assert c.identify() == "C major"


def test_save_midi_tone(tmp_path):
    from pytheory.play import save_midi
    path = tmp_path / "tone.mid"
    tone = Tone.from_string("C4", system="western")
    save_midi(tone, str(path))
    assert path.exists()
    data = path.read_bytes()
    assert data[:4] == b'MThd'


def test_save_midi_chord(tmp_path):
    from pytheory.play import save_midi
    path = tmp_path / "chord.mid"
    chord = Chord.from_symbol("Am")
    save_midi(chord, str(path))
    assert path.exists()
    data = path.read_bytes()
    assert data[:4] == b'MThd'


def test_save_midi_progression(tmp_path):
    from pytheory.play import save_midi
    path = tmp_path / "prog.mid"
    chords = Key("C", "major").progression("I", "V", "vi", "IV")
    save_midi(chords, str(path), t=500, bpm=120)
    assert path.exists()
    assert path.stat().st_size > 14  # header is 14 bytes


def test_save_midi_with_gap(tmp_path):
    from pytheory.play import save_midi
    path = tmp_path / "gap.mid"
    chords = Key("G", "major").progression("I", "IV", "V", "I")
    save_midi(chords, str(path), gap=100)
    assert path.exists()


def test_cli_midi_basic(capsys, tmp_path):
    from pytheory.cli import cmd_midi
    import argparse
    outfile = str(tmp_path / "test.mid")
    args = argparse.Namespace(
        tonic="C", mode="major", numerals=["I", "V", "vi", "IV"],
        output=outfile, bpm=120, duration=500
    )
    cmd_midi(args)
    out = capsys.readouterr().out
    assert "C major" in out
    assert "Output" in out
    import os
    assert os.path.exists(outfile)


def test_cli_midi_custom_bpm(capsys, tmp_path):
    from pytheory.cli import cmd_midi
    import argparse
    outfile = str(tmp_path / "test_bpm.mid")
    args = argparse.Namespace(
        tonic="G", mode="major", numerals=["I", "IV", "V"],
        output=outfile, bpm=90, duration=750
    )
    cmd_midi(args)
    out = capsys.readouterr().out
    assert "90" in out


def test_cli_midi_file_content(tmp_path):
    from pytheory.cli import cmd_midi
    import argparse
    outfile = str(tmp_path / "content.mid")
    args = argparse.Namespace(
        tonic="C", mode="major", numerals=["I", "V"],
        output=outfile, bpm=120, duration=500
    )
    cmd_midi(args)
    data = (tmp_path / "content.mid").read_bytes()
    assert data[:4] == b'MThd'


def test_cli_midi_minor(capsys, tmp_path):
    from pytheory.cli import cmd_midi
    import argparse
    outfile = str(tmp_path / "minor.mid")
    args = argparse.Namespace(
        tonic="A", mode="minor", numerals=["i", "IV", "V"],
        output=outfile, bpm=120, duration=500
    )
    cmd_midi(args)
    out = capsys.readouterr().out
    assert "A minor" in out


def test_score_save_midi(tmp_path):
    """save_midi writes a valid MIDI file header."""
    score = Score("4/4", bpm=120)
    score.add(Tone.from_string("C4"), Duration.QUARTER)
    score.add(Tone.from_string("E4"), Duration.QUARTER)
    score.rest(Duration.QUARTER)
    score.add(Tone.from_string("G4"), Duration.QUARTER)

    midi_path = tmp_path / "test.mid"
    score.save_midi(str(midi_path))

    data = midi_path.read_bytes()
    # Valid MIDI starts with MThd
    assert data[:4] == b"MThd"
    # Contains a track chunk
    assert b"MTrk" in data
    # File is non-trivial
    assert len(data) > 30


def test_pattern_midi_export(tmp_path):
    from pytheory import Pattern
    p = Pattern.preset("bossa nova")
    score = p.to_score(repeats=2, bpm=140)
    path = tmp_path / "bossa.mid"
    score.save_midi(str(path))
    data = path.read_bytes()
    assert data[:4] == b"MThd"
    assert len(data) > 50


def test_repl_save_midi(tmp_path):
    from pytheory.repl import Session, cmd_key, cmd_prog, cmd_save_midi
    s = Session()
    cmd_key(s, ["Am"])
    cmd_prog(s, ["i", "iv", "V", "i"])
    path = str(tmp_path / "test.mid")
    cmd_save_midi(s, [path])
    assert (tmp_path / "test.mid").exists()


def test_from_midi_basic(tmp_path):
    """Create a simple MIDI with save_midi, re-import with from_midi."""
    from pytheory import Score, Duration, Tone
    score = Score("4/4", bpm=120)
    score.add(Tone.from_string("C4"), Duration.QUARTER)
    score.add(Tone.from_string("E4"), Duration.QUARTER)
    score.add(Tone.from_string("G4"), Duration.QUARTER)

    midi_path = str(tmp_path / "basic.mid")
    score.save_midi(midi_path)

    imported = Score.from_midi(midi_path)
    # Should have at least one part with notes
    assert len(imported.parts) >= 1
    total_notes = sum(
        1 for p in imported.parts.values()
        for n in p.notes if n.tone is not None
    )
    assert total_notes == 3


def test_from_midi_tempo(tmp_path):
    """Verify BPM is preserved through save/import."""
    from pytheory import Score, Duration, Tone
    score = Score("4/4", bpm=140)
    score.add(Tone.from_string("A4"), Duration.QUARTER)

    midi_path = str(tmp_path / "tempo.mid")
    score.save_midi(midi_path)

    imported = Score.from_midi(midi_path)
    assert imported.bpm == 140


def test_from_midi_roundtrip(tmp_path):
    """Save a progression as MIDI, import it, check parts/notes."""
    from pytheory import Score, Duration, Tone
    score = Score("3/4", bpm=100)
    score.add(Tone.from_string("C4"), Duration.QUARTER)
    score.add(Tone.from_string("D4"), Duration.QUARTER)
    score.add(Tone.from_string("E4"), Duration.QUARTER)
    score.add(Tone.from_string("F4"), Duration.QUARTER)

    midi_path = str(tmp_path / "roundtrip.mid")
    score.save_midi(midi_path)

    imported = Score.from_midi(midi_path)
    assert imported.bpm == 100
    assert imported.time_signature == TimeSignature(3, 4)
    total_notes = sum(
        1 for p in imported.parts.values()
        for n in p.notes if n.tone is not None
    )
    assert total_notes == 4


def test_from_midi_velocity(tmp_path):
    """Verify velocity is preserved through save/import."""
    from pytheory import Score, Duration, Tone
    score = Score("4/4", bpm=120)
    # save_midi uses a fixed velocity param, default 100
    score.add(Tone.from_string("C4"), Duration.QUARTER)
    score.add(Tone.from_string("E4"), Duration.HALF)

    midi_path = str(tmp_path / "velocity.mid")
    score.save_midi(midi_path, velocity=80)

    imported = Score.from_midi(midi_path)
    sounding = [
        n for p in imported.parts.values()
        for n in p.notes if n.tone is not None
    ]
    assert len(sounding) == 2
    for n in sounding:
        assert n.velocity == 80


def test_from_midi_drums(tmp_path):
    """Verify drum hits survive a roundtrip."""
    from pytheory import Score, Pattern
    score = Score("4/4", bpm=120)
    score.add_pattern(Pattern.preset("rock"), repeats=1)

    midi_path = str(tmp_path / "drums.mid")
    score.save_midi(midi_path)

    imported = Score.from_midi(midi_path)
    assert len(imported._drum_hits) > 0


def test_from_midi_time_signature(tmp_path):
    """Verify time signature is preserved."""
    from pytheory import Score, Duration, Tone
    score = Score("6/8", bpm=150)
    score.add(Tone.from_string("C4"), Duration.QUARTER)

    midi_path = str(tmp_path / "timesig.mid")
    score.save_midi(midi_path)

    imported = Score.from_midi(midi_path)
    assert imported.time_signature == TimeSignature(6, 8)
    assert imported.bpm == 150


def test_from_midi_note_durations(tmp_path):
    """Verify note durations are approximately preserved."""
    from pytheory import Score, Duration, Tone
    score = Score("4/4", bpm=120)
    score.add(Tone.from_string("C4"), Duration.WHOLE)    # 4 beats
    score.add(Tone.from_string("E4"), Duration.HALF)     # 2 beats

    midi_path = str(tmp_path / "durations.mid")
    score.save_midi(midi_path)

    imported = Score.from_midi(midi_path)
    sounding = [
        n for p in imported.parts.values()
        for n in p.notes if n.tone is not None
    ]
    assert len(sounding) == 2
    assert abs(sounding[0].beats - 4.0) < 0.01
    assert abs(sounding[1].beats - 2.0) < 0.01


def test_from_midi_preserves_polyphony(tmp_path):
    """Simultaneous notes import as a Chord, not a flattened sequence."""
    from pytheory import Score, Tone
    from pytheory.rhythm import Note, _RawDuration
    from pytheory.chords import Chord

    score = Score("4/4", bpm=120)
    score.notes.append(Note(tone=Chord.from_symbol("C"), duration=_RawDuration(2.0)))
    score.notes.append(Note(tone=Chord.from_symbol("G7"), duration=_RawDuration(2.0)))

    midi_path = str(tmp_path / "poly.mid")
    score.save_midi(midi_path)

    imported = Score.from_midi(midi_path)
    chords = [
        n.tone for p in imported.parts.values()
        for n in p.notes if n.tone is not None
    ]
    assert len(chords) == 2
    # Both come back as multi-note chords, correctly identified.
    assert all(isinstance(c, Chord) for c in chords)
    assert chords[0].identify() == "C major"
    assert chords[1].identify() == "G dominant 7th"


def test_save_midi_includes_all_parts(tmp_path):
    """Multi-part scores must export every part, not just the default one."""
    from pytheory import Score, Tone
    from pytheory.chords import Chord

    score = Score("4/4", bpm=120)
    piano = score.part("piano")
    bass = score.part("bass")
    for sym, root in (("C", "C2"), ("G", "G2")):
        piano.add(Chord.from_symbol(sym), 4)
        bass.add(Tone.from_string(root), 4)

    midi_path = str(tmp_path / "multi.mid")
    score.save_midi(midi_path)

    imported = Score.from_midi(midi_path)
    sounding = [
        n.tone for p in imported.parts.values()
        for n in p.notes if n.tone is not None
    ]
    # 2 piano chords + 2 bass notes — none dropped on export.
    assert len(sounding) == 4
    assert sum(1 for t in sounding if isinstance(t, Chord)) == 2


def test_notation_hold_keeps_bars_aligned():
    """Part.hold() (overlap) notes must not push barlines out of place;
    the held pitch is folded into the next note as a chord."""
    score = Score("4/4", bpm=120)
    p = score.part("piano")
    p.hold("C3", Duration.WHOLE)     # 4-beat held bass under the melody
    p.add("E4", Duration.HALF)
    p.add("G4", Duration.HALF)

    # The held note merges into the next sounding note as a chord, so the
    # bar still totals 4 beats (chord 2 + G4 2), exactly one measure.
    abc_body = [l for l in score.to_abc().splitlines()
                if l and l[1:2] != ":"][-1]
    assert abc_body.count("|") == 1          # one barline → one measure
    assert "[" in abc_body                    # the held note became a chord

    ly = score.to_lilypond()
    assert "<c" in ly                         # chord present in LilyPond too


def test_notation_emits_articulations():
    """Staccato/accent/fermata reach LilyPond and MusicXML."""
    score = Score("4/4", bpm=120)
    p = score.part("lead")
    p.notes.append(RhythmNote(tone=Tone.from_string("C4"),
                              duration=Duration.QUARTER, articulation="staccato"))
    p.notes.append(RhythmNote(tone=Tone.from_string("E4"),
                              duration=Duration.HALF, articulation="fermata"))

    ly = score.to_lilypond()
    assert "-." in ly and "\\fermata" in ly

    mxl = score.to_musicxml()
    assert "<staccato" in mxl and "<fermata" in mxl


def test_render_hybrid_part_keeps_melodic_notes():
    """A part with both notes and drum hits must still render its notes."""
    import numpy
    from pytheory import Score, Duration, DrumSound
    from pytheory.play import render_score

    def rms(buf):
        return float(numpy.sqrt(numpy.mean(buf.astype(numpy.float64) ** 2)))

    # Notes-only part (not classified as drums).
    a = Score("4/4", bpm=120)
    pa = a.part("lead", synth="saw")
    pa.add("C4", Duration.WHOLE)
    notes_only = rms(render_score(a))

    # Same notes plus a drum hit -> is_drums becomes True.
    b = Score("4/4", bpm=120)
    pb = b.part("lead", synth="saw")
    pb.add("C4", Duration.WHOLE)
    pb.hit(DrumSound.KICK, Duration.QUARTER)
    hybrid = rms(render_score(b))

    # Before the fix the notes were silently dropped, leaving only a brief
    # kick -> hybrid RMS would collapse far below the sustained note.
    assert hybrid >= notes_only * 0.8


def test_save_midi_drums_survive_split(tmp_path):
    """drums(split=True) moves hits into group parts; export must find them."""
    from pytheory import Score, Pattern

    score = Score("4/4", bpm=120)
    score.add_pattern(Pattern.preset("rock"), repeats=2)
    score._split_drums()                       # hits now live in kick/snare/hats
    assert len(score._drum_hits) == 0          # the proxy 'drums' part is empty

    midi_path = str(tmp_path / "split.mid")
    score.save_midi(midi_path)

    imported = Score.from_midi(midi_path)
    # Before the fix this round-tripped to zero drums.
    assert len(imported._drum_hits) > 0


def test_from_midi_single_notes_stay_single(tmp_path):
    """A sequential melody must not be mis-grouped into chords."""
    from pytheory import Score, Duration, Tone
    score = Score("4/4", bpm=120)
    for name in ("C4", "D4", "E4", "F4"):
        score.add(Tone.from_string(name), Duration.QUARTER)

    midi_path = str(tmp_path / "melody.mid")
    score.save_midi(midi_path)

    imported = Score.from_midi(midi_path)
    sounding = [
        n.tone for p in imported.parts.values()
        for n in p.notes if n.tone is not None
    ]
    assert len(sounding) == 4
    assert all(isinstance(t, Tone) for t in sounding)


def test_to_lilypond_default_has_no_chord_contexts():
    # Default output: plain notation staves, no chord contexts/diagrams.
    out = _progression_score().to_lilypond()
    assert out.startswith('\\version "2.24.0"')
    for marker in ("chordProg", "ChordNames", "FretBoards", "TabStaff",
                   "storePredefinedDiagram"):
        assert marker not in out
    assert out.endswith("  >>\n  \\layout { }\n}\n")


def test_to_lilypond_chord_names():
    out = _progression_score().to_lilypond(chord_names=True)
    assert "chordProg = \\chordmode { c1 g1 a1:m f1 }" in out
    assert "\\new ChordNames \\chordProg" in out
    assert "\\new FretBoards" not in out


def test_to_lilypond_fretboards_explicit_diagrams():
    out = _progression_score().to_lilypond(fretboards=True)
    assert "\\new FretBoards \\chordProg" in out
    # PyTheory's own C voicing (x32010) emitted as a predefined diagram.
    assert ('\\storePredefinedDiagram #default-fret-table \\chordmode {c} '
            '#guitar-tuning #"x;3;2;0;1;0;"') in out
    assert out.count("storePredefinedDiagram") == 4


def test_to_lilypond_tab():
    out = _progression_score().to_lilypond(tab=True)
    assert "\\new TabStaff \\chordProg" in out


def test_to_lilypond_chord_part_selects_named_part():
    from pytheory import Score, Key, Duration
    score = Score("4/4", bpm=120)
    score.part("piano")  # also a chord part, but we want "comp"
    comp = score.part("comp")
    for c in Key("G", "major").progression("I", "IV", "V", "I"):
        comp.add(c, Duration.WHOLE)
    out = score.to_lilypond(chord_names=True, chord_part="comp")
    assert "chordProg = \\chordmode { g1 c1 d1 g1 }" in out


def test_chord_to_chordmode_qualities():
    from pytheory import Chord, Score
    cases = {
        "C": ("c", ""), "Am": ("a", ":m"), "G7": ("g", ":7"),
        "Fmaj7": ("f", ":maj7"), "Dm7": ("d", ":m7"), "Bdim": ("b", ":dim"),
        "Caug": ("c", ":aug"), "Am7b5": ("a", ":m7.5-"),
    }
    for sym, expected in cases.items():
        assert Score._chord_to_chordmode(Chord.from_symbol(sym)) == expected


@pytest.mark.slow
def test_to_lilypond_compiles_with_lilypond(tmp_path):
    import shutil
    import subprocess
    if not shutil.which("lilypond"):
        pytest.skip("lilypond not on PATH")
    src = tmp_path / "leadsheet.ly"
    src.write_text(_progression_score().to_lilypond(
        chord_names=True, fretboards=True, tab=True))
    result = subprocess.run(
        ["lilypond", "-dno-point-and-click", "-o", str(tmp_path / "out"), str(src)],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "out.pdf").exists()
