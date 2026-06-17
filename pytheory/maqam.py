"""Arabic maqamat — the named melodic modes of Arabic, Turkish, and
related music, in their real quarter-tone (just) intonation.

A *maqam* is more than a scale. It's built from **ajnas** (sing. *jins*),
the trichord/tetrachord cells that stack into the full mode, and it has a
**seyir**, the conventional way a melody moves through it (where it
starts, where it rests, whether it favours the ascent or the descent).
Most of all, a maqam is defined by notes a piano can't play: the
**half-flats**, the neutral 2nds, 3rds, 6ths and 7ths that sit a
quarter-tone away from the tempered grid. Rast's third (a neutral 27/22,
~355 cents) is the sound of the whole tradition, and it lives in the
crack between E-flat and E.

This module encodes the best-known maqamat with their scale degrees, the
ajnas they're built from, the seyir, and — crucially — the 5-limit /
quarter-tone ratios, so they render in true intonation rather than
snapped to 12-TET.

Degrees are positions in the Do-based Arabic layout (Do = the tonic);
``↓`` marks a quarter-flat. Like a raga, the tonic is movable.

Example::

    >>> from pytheory import Maqam
    >>> rast = Maqam.get("rast")
    >>> rast.degree_names()
    ['Do', 'Re', 'Mi↓', 'Fa', 'Sol', 'La', 'Si↓']
    >>> rast.maqam_table("C")[2]["cents_off"]      # the neutral 3rd
    -45.5
    >>> rast.play("C")                              # oud, just intonation
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Optional

from .ragas import _JustNote

# Just ratios for each position in the Do-based maqam layout (the ones the
# catalogued maqamat use). The neutral (Zalzalian) steps are the quarter
# tones that 12-TET can't reach.
_MAQAM_JI = {
    0: Fraction(1, 1),      # Do        unison
    2: Fraction(16, 15),    # Reb       minor 2nd
    3: Fraction(12, 11),    # Re↓       neutral 2nd
    4: Fraction(9, 8),      # Re        major 2nd
    6: Fraction(6, 5),      # Mib       minor 3rd
    7: Fraction(27, 22),    # Mi↓       neutral 3rd  ← the Rast note
    8: Fraction(5, 4),      # Mi        major 3rd
    9: Fraction(4, 3),      # Fa        perfect 4th
    11: Fraction(45, 32),   # Fa#       augmented 4th
    13: Fraction(3, 2),     # Sol       perfect 5th
    15: Fraction(8, 5),     # Lab       minor 6th
    16: Fraction(18, 11),   # La↓       neutral 6th
    17: Fraction(5, 3),     # La        major 6th
    19: Fraction(16, 9),    # Sib       minor 7th
    20: Fraction(11, 6),    # Si↓       neutral 7th  ← the awj
    21: Fraction(15, 8),    # Si        major 7th
    24: Fraction(2, 1),     # Do'       octave
}

# Arabic note name for each layout position (Do = tonic).
_MAQAM_NAME = {
    0: "Do", 2: "Reb", 3: "Re↓", 4: "Re", 6: "Mib", 7: "Mi↓", 8: "Mi",
    9: "Fa", 11: "Fa#", 13: "Sol", 15: "Lab", 16: "La↓", 17: "La",
    19: "Sib", 20: "Si↓", 21: "Si", 24: "Do'",
}

_FLAT12 = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]


class Maqam:
    """An Arabic maqam: its scale, ajnas, seyir, and quarter-tone tuning.

    Attributes:
        name: the maqam's name.
        family: the maqam family (fasila) it belongs to.
        degrees: scale positions in the Do-based layout (tonic = ``0``).
        ajnas: the jins cells it's built from.
        seyir: how a melody conventionally moves through it.
        mood: its emotional character.
        aka: alternative names.
    """

    def __init__(self, name, *, family, degrees, ajnas, seyir, mood,
                 aka=None):
        self.name = name
        self.family = family
        self.degrees = list(degrees)
        self.ajnas = ajnas
        self.seyir = seyir
        self.mood = mood
        self.aka = aka or []

    # ── degrees & names ──────────────────────────────────────────────

    def degree_names(self) -> list[str]:
        """The ascending scale as Arabic note names (``↓`` = quarter-flat)."""
        return [_MAQAM_NAME[d] for d in self.degrees]

    @property
    def has_quartertones(self) -> bool:
        """Whether the maqam uses any neutral (quarter-tone) degree."""
        return any(d in (3, 7, 16, 20) for d in self.degrees)

    def note_names(self, tonic="C") -> list[str]:
        """Nearest 12-TET note names in the key of *tonic*.

        Quarter-tones round to the closest piano key, so half-flats lose
        their bend here — use :meth:`maqam_table` or :meth:`play` for the
        true intonation.
        """
        from .tones import Tone
        base = Tone.from_string(f"{tonic}4", system="western").midi
        out = []
        for d in self.degrees:
            semis = round(1200 * math.log2(float(_MAQAM_JI[d])) / 100)
            out.append(_FLAT12[(base + semis) % 12])
        return out

    # ── just intonation (quarter-tones) ──────────────────────────────

    def just_ratios(self) -> dict:
        """Each degree's just ratio from the tonic (keyed by Arabic name)."""
        return {_MAQAM_NAME[d]: _MAQAM_JI[d] for d in self.degrees}

    def maqam_table(self, tonic="C") -> list[dict]:
        """Per-degree tuning: ratio, ≈ note, Hz, and cents off 12-TET.

        The neutral degrees come out tens of cents from the piano — that
        gap *is* the maqam.
        """
        from .tones import Tone
        sa = Tone.from_string(f"{tonic}4", system="western")
        rows = []
        for d in self.degrees:
            ratio = _MAQAM_JI[d]
            cents = 1200 * math.log2(float(ratio))
            nearest = round(cents / 100)
            rows.append({
                "degree": _MAQAM_NAME[d],
                "ratio": f"{ratio.numerator}/{ratio.denominator}",
                "note": _FLAT12[(sa.midi + nearest) % 12],
                "hz": round(sa.frequency * float(ratio), 2),
                "cents_off": round(cents - nearest * 100, 1),
            })
        return rows

    def just_frequencies(self, tonic="C4") -> list[float]:
        """The ascending then descending run, just-intoned (Hz)."""
        from .tones import Tone
        if not isinstance(tonic, Tone):
            tonic = Tone.from_string(
                tonic if any(c.isdigit() for c in str(tonic)) else f"{tonic}4",
                system="western")
        hz = tonic.frequency
        up = [hz * float(_MAQAM_JI[d]) for d in self.degrees]
        up.append(hz * 2.0)                      # the octave
        return up + up[-2::-1]                   # add the descent

    def render(self, tonic="C4", *, synth="oud", t=420, envelope="pluck",
               reverb=0.3):
        """Render the ascending→descending run to a mono sample buffer.

        Quarter-tone accurate (the half-flats are voiced where they
        actually sit), with a reverb tail tying the phrase together.
        Returns a NumPy array (no audio device needed).
        """
        import numpy
        from .play import _render, _apply_reverb, Synth, Envelope, SAMPLE_RATE
        s = Synth[synth.upper()]
        env = Envelope[envelope.upper()]
        buffers = [_render(_JustNote(hz), synth=s, t=t, envelope=env)
                   for hz in self.just_frequencies(tonic)]
        buf = numpy.concatenate(buffers).astype(numpy.float32)
        if reverb and reverb > 0:
            tail = numpy.zeros(int(SAMPLE_RATE * 1.5), dtype=numpy.float32)
            buf = _apply_reverb(numpy.concatenate([buf, tail]), mix=reverb)
        return buf

    def play(self, tonic="C4", *, synth="oud", t=420, envelope="pluck",
             reverb=0.3):
        """Play the maqam (ascending then descending) in just intonation.

        Defaults to the oud voice. Like a raga, this is quarter-tone
        accurate — the half-flats are voiced where they actually sit.
        """
        from .play import _play_for, SAMPLE_RATE
        buf = self.render(tonic, synth=synth, t=t, envelope=envelope,
                          reverb=reverb)
        _play_for(buf, ms=int(len(buf) / SAMPLE_RATE * 1000))

    # ── lookup ───────────────────────────────────────────────────────

    @classmethod
    def get(cls, name: str) -> "Maqam":
        key = name.lower().replace(" ", "").replace("-", "")
        for m in _MAQAMS.values():
            cands = [m.name] + list(m.aka)
            if any(key == c.lower().replace(" ", "").replace("-", "")
                   for c in cands):
                return m
        raise KeyError(f"Unknown maqam: {name!r}. Try Maqam.names().")

    @classmethod
    def all(cls) -> list["Maqam"]:
        return [_MAQAMS[k] for k in sorted(_MAQAMS)]

    @classmethod
    def names(cls) -> list[str]:
        return sorted(m.name for m in _MAQAMS.values())

    @classmethod
    def by_family(cls, family: str) -> list["Maqam"]:
        f = family.lower()
        return [m for m in cls.all() if m.family.lower() == f]

    def __repr__(self) -> str:
        return f"<Maqam {self.name} (family {self.family})>"

    def __str__(self) -> str:
        return self.name


# ── the maqamat ──────────────────────────────────────────────────────
# Common forms, with the tonic set to Do (C). Ajnas and seyir follow the
# mainstream (Egyptian/Levantine) practice; regional variants exist.

_MAQAM_LIST = [
    Maqam("Rast", family="Rast",
          degrees=[0, 4, 7, 9, 13, 17, 20],
          ajnas="Jins Rast on Do + Jins Rast on Sol",
          seyir="ascending from the tonic; rests on Sol and the neutral 3rd",
          mood="dignified, sober, the 'mother' maqam"),
    Maqam("Bayati", family="Bayati",
          degrees=[0, 3, 6, 9, 13, 15, 19],
          ajnas="Jins Bayati on Do + Jins Nahawand on Sol",
          seyir="from the tonic; the neutral 2nd is its signature",
          mood="tender, intimate, the everyday maqam", aka=["Bayat"]),
    Maqam("Hijaz", family="Hijaz",
          degrees=[0, 2, 8, 9, 13, 15, 19],
          ajnas="Jins Hijaz on Do + Jins Rast/Nahawand on Sol",
          seyir="ascending; the augmented 2nd (Reb→Mi) is the colour",
          mood="yearning, devotional, desert-evening"),
    Maqam("Nahawand", family="Nahawand",
          degrees=[0, 4, 6, 9, 13, 15, 19],
          ajnas="Jins Nahawand on Do + Jins Hijaz/Kurd on Sol",
          seyir="the Arabic minor; ascends, raising the 7th in cadence",
          mood="romantic, wistful", aka=["Nihavend"]),
    Maqam("Kurd", family="Kurd",
          degrees=[0, 2, 6, 9, 13, 15, 19],
          ajnas="Jins Kurd on Do + Jins Kurd on Sol",
          seyir="Phrygian colour; from the tonic",
          mood="plaintive, modern", aka=["Kurdi"]),
    Maqam("Ajam", family="Ajam",
          degrees=[0, 4, 8, 9, 13, 17, 21],
          ajnas="Jins Ajam on Do + Jins Ajam on Sol",
          seyir="the major scale; bright and direct",
          mood="bright, celebratory", aka=["Ajam Ushayran"]),
    Maqam("Hijazkar", family="Hijaz",
          degrees=[0, 2, 8, 9, 13, 15, 21],
          ajnas="Jins Hijaz on Do + Jins Hijaz on Sol",
          seyir="symmetric double-Hijaz; descending tendency",
          mood="dramatic, ornate", aka=["Shahnaz", "Shedaraban relative"]),
    Maqam("Saba", family="Saba",
          degrees=[0, 3, 6, 8, 13, 15, 19],
          ajnas="Jins Saba on Do (its diminished 4th is unmistakable)",
          seyir="from the tonic; the lowered 4th gives its grief",
          mood="sorrowful, aching, the maqam of lament"),
    Maqam("Suznak", family="Rast",
          degrees=[0, 4, 7, 9, 13, 15, 21],
          ajnas="Jins Rast on Do + Jins Hijaz on Sol",
          seyir="Rast below, Hijaz above; ascending",
          mood="warm then yearning"),
    Maqam("Nakriz", family="Nahawand",
          degrees=[0, 4, 6, 11, 13, 17, 19],
          ajnas="Jins Nakriz on Do (minor with a raised 4th)",
          seyir="the raised 4th pulls toward the 5th",
          mood="mysterious, restless", aka=["Nigriz"]),
]

_MAQAMS = {m.name.lower(): m for m in _MAQAM_LIST}
