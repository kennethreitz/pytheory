"""Hindustani ragas — the living melodic forms of North Indian classical music.

A *thaat* is a parent scale; a *raga* is what musicians actually play. A
raga is more than its notes: it has an ascending line (*aroha*) and a
descending line (*avaroha*) that often differ, a characteristic catch-
phrase (*pakad*) that identifies it in a few notes, a most-important note
(*vadi*) and its second (*samvadi*), a time of day or season it belongs
to, and an emotional flavour (*rasa*).

This module encodes a representative set of the best-known ragas. Swaras
are written in the usual ASCII sargam:

    S   Sa  (tonic)
    r/R komal / shuddha Re        g/G komal / shuddha Ga
    m/M shuddha / tivra  Ma       P   Pa
    d/D komal / shuddha Dha       n/N komal / shuddha Ni

A trailing ``'`` raises a swara an octave, a trailing ``.`` lowers it.
Lowercase is komal (flattened), uppercase is shuddha (natural), and ``M``
is tivra (sharpened) Ma.

Ragas vary by gharana and region; these are common, widely-taught forms.

Example::

    >>> from pytheory import Raga
    >>> yaman = Raga.get("yaman")
    >>> yaman.aroha_swaras()
    ['N.', 'R', 'G', 'M', 'D', 'N', "S'"]
    >>> [t.name for t in yaman.scale_tones("C")]
    ['C', 'D', 'E', 'F#', 'G', 'A', 'B']
    >>> yaman.time, yaman.rasa
    ('evening', 'serene, romantic')
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Optional

# Semitone offset of each swara from Sa.
_SWARA = {
    "S": 0, "r": 1, "R": 2, "g": 3, "G": 4, "m": 5,
    "M": 6, "P": 7, "d": 8, "D": 9, "n": 10, "N": 11,
}
# Canonical ascending order for listing a raga's distinct swaras.
_SWARA_ORDER = ["S", "r", "R", "g", "G", "m", "M", "P", "d", "D", "n", "N"]

# Just-intonation ratio of each swara from Sa — the 5-limit intervals of
# the shruti system, the intonation a raga is actually meant to be sung
# in (and what the bundled "shruti" tone system encodes). These are what
# make a komal Ga or a tivra Ma sound "right" rather than the tempered
# 12-TET approximation.
_SWARA_JI = {
    "S": Fraction(1, 1), "r": Fraction(16, 15), "R": Fraction(9, 8),
    "g": Fraction(6, 5), "G": Fraction(5, 4), "m": Fraction(4, 3),
    "M": Fraction(45, 32), "P": Fraction(3, 2), "d": Fraction(8, 5),
    "D": Fraction(5, 3), "n": Fraction(16, 9), "N": Fraction(15, 8),
}


def _parse(token: str) -> Optional[int]:
    """Parse one sargam token to a semitone offset from Sa (or None)."""
    clean = token.replace(",", "").replace("|", "").strip()
    if not clean:
        return None
    letter = clean[0]
    if letter not in _SWARA:
        return None
    offset = _SWARA[letter]
    for ch in clean[1:]:
        if ch == "'":
            offset += 12
        elif ch == ".":
            offset -= 12
    return offset


def _swaras(line: str) -> list[str]:
    """Split a sargam line into clean swara tokens."""
    out = []
    for tok in line.split():
        clean = tok.replace(",", "").replace("|", "").strip()
        if clean and clean[0] in _SWARA:
            out.append(clean)
    return out


class _JustNote:
    """A bare frequency that renders through the normal synth/envelope path.

    ``_render`` asks a note for ``.pitch()`` and iterates ``.tones``; this
    shim answers with an exact just-intoned frequency, so a raga can be
    voiced microtonally without snapping to 12-TET.
    """
    def __init__(self, hz: float):
        self._hz = hz

    @property
    def tones(self):
        return [self]

    def pitch(self, **_):
        return self._hz


class Raga:
    """A Hindustani raga: its melodic rules, mood, and time.

    Attributes:
        name: the raga's name.
        thaat: parent scale (one of the ten thaats).
        aroha: ascending line (sargam string).
        avaroha: descending line (sargam string).
        pakad: characteristic identifying phrase (sargam string).
        vadi: the most important (sonant) swara.
        samvadi: the second-most important (consonant) swara.
        time: the time of day (or season) the raga belongs to.
        rasa: its emotional flavour.
        jati: how many distinct swaras ascend / descend.
        aka: alternative names.
    """

    def __init__(self, name, *, thaat, aroha, avaroha, vadi, samvadi,
                 time, rasa, pakad=None, aka=None, tradition="hindustani"):
        self.name = name
        # The parent scale: a thaat for Hindustani ragas, a melakarta for
        # Carnatic ones.
        self.thaat = thaat
        self.tradition = tradition
        self.aroha = aroha
        self.avaroha = avaroha
        self.pakad = pakad
        self.vadi = vadi
        self.samvadi = samvadi
        self.time = time
        self.rasa = rasa
        self.aka = aka or []

    # ── sargam access ────────────────────────────────────────────────

    def aroha_swaras(self) -> list[str]:
        """The ascending line as a list of sargam tokens."""
        return _swaras(self.aroha)

    def avaroha_swaras(self) -> list[str]:
        """The descending line as a list of sargam tokens."""
        return _swaras(self.avaroha)

    def pakad_swaras(self) -> list[str]:
        """The identifying phrase as sargam tokens (empty if none)."""
        return _swaras(self.pakad) if self.pakad else []

    @property
    def swara_set(self) -> list[str]:
        """The distinct swaras the raga uses, in ascending order."""
        used = set()
        for line in (self.aroha, self.avaroha):
            for tok in _swaras(line):
                base = tok[0]
                # Keep the accidental letter (r vs R), drop octave marks.
                used.add(base)
        return [s for s in _SWARA_ORDER if s in used]

    @property
    def jati(self) -> str:
        """Classification by ascending/descending note counts."""
        names = {5: "audav", 6: "shadav", 7: "sampurna"}
        a = len({t[0] for t in self.aroha_swaras()})
        d = len({t[0] for t in self.avaroha_swaras()})
        return f"{names.get(a, a)}-{names.get(d, d)}"

    # ── pitched output ───────────────────────────────────────────────

    def _tones(self, line: str, sa):
        from .tones import Tone
        if not isinstance(sa, Tone):
            sa = Tone.from_string(sa if any(c.isdigit() for c in str(sa))
                                  else f"{sa}4", system="western")
        tones = []
        for tok in line.split():
            off = _parse(tok)
            if off is not None:
                tones.append(sa.add(off))
        return tones

    def aroha_tones(self, sa="C4") -> list:
        """The ascending line as :class:`Tone` objects, with Sa = *sa*."""
        return self._tones(self.aroha, sa)

    def avaroha_tones(self, sa="C4") -> list:
        """The descending line as :class:`Tone` objects, with Sa = *sa*."""
        return self._tones(self.avaroha, sa)

    def pakad_tones(self, sa="C4") -> list:
        """The pakad as :class:`Tone` objects (empty if none)."""
        return self._tones(self.pakad, sa) if self.pakad else []

    def scale_tones(self, sa="C") -> list:
        """The raga's distinct tones in one octave, ascending from Sa."""
        from .tones import Tone
        base = Tone.from_string(f"{sa}4" if not any(c.isdigit() for c in str(sa))
                                else str(sa), system="western")
        return [base.add(_SWARA[s]) for s in self.swara_set]

    def note_names(self, sa="C") -> list[str]:
        """The raga's distinct note names in the key of *sa*."""
        return [t.name for t in self.scale_tones(sa)]

    def melody(self, sa="C4") -> list:
        """Aroha then avaroha as one :class:`Tone` line — a quick run."""
        return self.aroha_tones(sa) + self.avaroha_tones(sa)[1:]

    # ── just intonation (shruti) ─────────────────────────────────────

    def just_ratios(self) -> dict:
        """Each distinct swara's just-intonation ratio from Sa.

        These are the shruti intervals — 5-limit ratios like 5/4 for Ga
        and 45/32 for tivra Ma — that the raga is meant to be intoned
        in, rather than the tempered 12-TET grid.

        Example::

            >>> Raga.get("yaman").just_ratios()["G"]
            Fraction(5, 4)
        """
        return {s: _SWARA_JI[s] for s in self.swara_set}

    def _just_hz(self, line: str, sa) -> list[float]:
        from .tones import Tone
        if not isinstance(sa, Tone):
            sa = Tone.from_string(sa if any(c.isdigit() for c in str(sa))
                                  else f"{sa}4", system="western")
        sa_hz = sa.frequency
        out = []
        for tok in line.split():
            clean = tok.replace(",", "").replace("|", "").strip()
            if not clean or clean[0] not in _SWARA_JI:
                continue
            ratio = _SWARA_JI[clean[0]]
            for ch in clean[1:]:
                if ch == "'":
                    ratio *= 2
                elif ch == ".":
                    ratio /= 2
            out.append(sa_hz * float(ratio))
        return out

    def just_frequencies(self, sa="C4") -> list[float]:
        """The aroha→avaroha run as just-intoned frequencies (Hz).

        Sa is movable: it's pinned to *sa* and the shruti ratios are
        built on top, so you get authentic intonation in any key.
        """
        return (self._just_hz(self.aroha, sa)
                + self._just_hz(self.avaroha, sa)[1:])

    def shruti_table(self, sa="C") -> list[dict]:
        """Per-swara intonation detail: ratio, Hz, and cents off 12-TET.

        Shows how far each shruti sits from the tempered piano — e.g.
        the just major 3rd (Ga, 5/4) is ~14 cents flatter than the
        equal-tempered E.
        """
        from .tones import Tone
        sa_tone = Tone.from_string(
            f"{sa}4" if not any(c.isdigit() for c in str(sa)) else str(sa),
            system="western")
        sa_hz = sa_tone.frequency
        rows = []
        for s in self.swara_set:
            ratio = _SWARA_JI[s]
            ji_cents = 1200 * math.log2(float(ratio))
            cents_off = ji_cents - _SWARA[s] * 100
            rows.append({
                "swara": s,
                "ratio": f"{ratio.numerator}/{ratio.denominator}",
                "note": sa_tone.add(_SWARA[s]).name,
                "hz": round(sa_hz * float(ratio), 2),
                "cents_off": round(cents_off, 1),
            })
        return rows

    def render(self, sa="C4", *, synth="sitar", t=420, envelope="pluck",
               just=True, reverb=0.35):
        """Render the aroha→avaroha run to a mono sample buffer.

        Notes are laid end to end and a hall reverb is mixed over the
        whole phrase, so the tail of one swara bleeds into the next —
        much closer to how a raga actually breathes than dry, separate
        notes. Returns a NumPy array (no audio device needed).

        Args:
            sa: the tonic for Sa.
            synth: waveform name (default sitar).
            t: duration per swara in ms.
            envelope: ADSR preset name.
            just: just intonation (True, default) vs tempered 12-TET.
            reverb: wet mix 0..1 (0 disables); default 0.35.
        """
        import numpy
        from .play import _render, _apply_reverb, Synth, Envelope, SAMPLE_RATE

        s = Synth[synth.upper()]
        env = Envelope[envelope.upper()]
        if just:
            notes = [_JustNote(hz) for hz in self.just_frequencies(sa)]
        else:
            notes = self.melody(sa)

        buffers = [_render(n, synth=s, t=t, envelope=env) for n in notes]
        buf = numpy.concatenate(buffers).astype(numpy.float32)

        if reverb and reverb > 0:
            # Pad so the reverb tail isn't clipped off the end.
            tail = numpy.zeros(int(SAMPLE_RATE * 1.5), dtype=numpy.float32)
            buf = _apply_reverb(numpy.concatenate([buf, tail]), mix=reverb)
        return buf

    def play(self, sa="C4", *, synth="sitar", t=420, envelope="pluck",
             just=True, reverb=0.35):
        """Play the aroha then avaroha through the speakers.

        Defaults to the sitar voice in **just intonation** (the shruti
        tuning a raga is meant to be heard in), with a touch of reverb so
        the phrase rings like a hall. Pass ``just=False`` for tempered
        12-TET, ``reverb=0`` for a dry run, or any synth name you like.
        """
        from .play import _play_for, SAMPLE_RATE
        buf = self.render(sa, synth=synth, t=t, envelope=envelope,
                          just=just, reverb=reverb)
        _play_for(buf, ms=int(len(buf) / SAMPLE_RATE * 1000))

    # ── lookup ───────────────────────────────────────────────────────

    @classmethod
    def get(cls, name: str) -> "Raga":
        """Look up a raga by name (case-insensitive, ignores spaces)."""
        key = name.lower().replace(" ", "").replace("-", "")
        for raga in _RAGAS.values():
            cands = [raga.name] + list(raga.aka)
            if any(key == c.lower().replace(" ", "").replace("-", "")
                   for c in cands):
                return raga
        raise KeyError(f"Unknown raga: {name!r}. "
                       f"Try Raga.names() for the list.")

    @classmethod
    def all(cls) -> list["Raga"]:
        """Every raga, sorted by name."""
        return [_RAGAS[k] for k in sorted(_RAGAS)]

    @classmethod
    def names(cls) -> list[str]:
        """The names of every known raga, sorted."""
        return sorted(r.name for r in _RAGAS.values())

    @classmethod
    def by_thaat(cls, thaat: str) -> list["Raga"]:
        """Every raga belonging to the given thaat."""
        t = thaat.lower()
        return [r for r in cls.all() if r.thaat.lower() == t]

    @classmethod
    def by_time(cls, period: str) -> list["Raga"]:
        """Ragas whose time of day matches (substring, case-insensitive)."""
        p = period.lower()
        return [r for r in cls.all() if p in r.time.lower()]

    @classmethod
    def by_tradition(cls, tradition: str) -> list["Raga"]:
        """Ragas of a tradition — ``"hindustani"`` or ``"carnatic"``."""
        t = tradition.lower()
        return [r for r in cls.all() if r.tradition.lower() == t]

    def __repr__(self) -> str:
        return f"<Raga {self.name} (thaat {self.thaat}, {self.time})>"

    def __str__(self) -> str:
        return self.name


# ── the ragas ────────────────────────────────────────────────────────
# Common, widely-taught forms. Lowercase swara = komal, uppercase =
# shuddha, M = tivra Ma; trailing ' = upper octave, . = lower octave.

_RAGA_LIST = [
    Raga("Yaman", thaat="kalyan",
         aroha="N. R G M D N S'", avaroha="S' N D P M G R S",
         pakad="N. R G, R, P M G R S", vadi="G", samvadi="N",
         time="evening", rasa="serene, romantic", aka=["Kalyan"]),
    Raga("Bilawal", thaat="bilawal",
         aroha="S R G m P D N S'", avaroha="S' N D P m G R S",
         pakad="G R, G P, m G R S", vadi="D", samvadi="G",
         time="morning", rasa="cheerful, devotional"),
    Raga("Khamaj", thaat="khamaj",
         aroha="S G m P D N S'", avaroha="S' n D P m G R S",
         pakad="G m P D, m G, P D n D, m G", vadi="G", samvadi="N",
         time="night", rasa="romantic, light"),
    Raga("Kafi", thaat="kafi",
         aroha="S R g m P D n S'", avaroha="S' n D P m g R S",
         pakad="S R g, g m, P, D n D P", vadi="P", samvadi="S",
         time="night", rasa="playful, spring"),
    Raga("Asavari", thaat="asavari",
         aroha="S R m P d S'", avaroha="S' n d P m g R S",
         pakad="R m P, d, m P g R S", vadi="d", samvadi="g",
         time="late morning", rasa="renunciation, pathos"),
    Raga("Bhairavi", thaat="bhairavi",
         aroha="S r g m P d n S'", avaroha="S' n d P m g r S",
         pakad="S, g m P, g r S", vadi="m", samvadi="S",
         time="morning", rasa="devotional, compassion"),
    Raga("Bhairav", thaat="bhairav",
         aroha="S r G m P d N S'", avaroha="S' N d P m G r S",
         pakad="S r S, d. N. S, G m P, d P", vadi="d", samvadi="r",
         time="dawn", rasa="serious, peaceful, devotional"),
    Raga("Todi", thaat="todi",
         aroha="S r g M P d N S'", avaroha="S' N d P M g r S",
         pakad="d. N. S r g, r g r S", vadi="d", samvadi="g",
         time="late morning", rasa="intense, yearning",
         aka=["Miyan ki Todi"]),
    Raga("Marwa", thaat="marwa",
         aroha="S r G M D N S'", avaroha="S' N D M G r S",
         pakad="D. N. r S, D. r G M G r S", vadi="r", samvadi="D",
         time="sunset", rasa="anticipation, restlessness"),
    Raga("Purvi", thaat="purvi",
         aroha="S r G M P d N S'", avaroha="S' N d P M G r S",
         pakad="N. r G, M G, M d, P", vadi="G", samvadi="N",
         time="sunset", rasa="serious, mystical", aka=["Poorvi"]),
    Raga("Bhimpalasi", thaat="kafi",
         aroha="n. S g m P n S'", avaroha="S' n D P m g R S",
         pakad="n. S m, g m, P, m g R S", vadi="m", samvadi="S",
         time="afternoon", rasa="longing, devotion",
         aka=["Bhimpalas", "Bheempalasi"]),
    Raga("Bhupali", thaat="kalyan",
         aroha="S R G P D S'", avaroha="S' D P G R S",
         pakad="G R S D., S R G, P G", vadi="G", samvadi="D",
         time="evening", rasa="peaceful, devotional",
         aka=["Bhoop", "Bhup"]),
    Raga("Malkauns", thaat="bhairavi",
         aroha="S g m d n S'", avaroha="S' n d m g S",
         pakad="m g, m d n d, m g S", vadi="m", samvadi="S",
         time="late night", rasa="meditative, profound",
         aka=["Malkosh", "Malkounts"]),
    Raga("Durga", thaat="bilawal",
         aroha="S R m P D S'", avaroha="S' D P m R S",
         pakad="S R m, P D, m R, P D S'", vadi="m", samvadi="S",
         time="night", rasa="devotional, valour"),
    Raga("Desh", thaat="khamaj",
         aroha="S R m P N S'", avaroha="S' n D P m G R S",
         pakad="R m P, n D P, m G R", vadi="R", samvadi="P",
         time="night", rasa="patriotic, monsoon", aka=["Des"]),
    Raga("Bageshri", thaat="kafi",
         aroha="S g m D n S'", avaroha="S' n D m g R S",
         pakad="S g m D, n D, m g R S", vadi="m", samvadi="S",
         time="late night", rasa="longing, union",
         aka=["Bageshree", "Bagesri"]),
    Raga("Darbari Kanada", thaat="asavari",
         aroha="S R g m P d n S'", avaroha="S' d n P m P g m R S",
         pakad="R g g S, d. n. S R, P", vadi="R", samvadi="P",
         time="midnight", rasa="majestic, serious",
         aka=["Darbari", "Darbari Kanada"]),
    Raga("Hamsadhwani", thaat="bilawal",
         aroha="S R G P N S'", avaroha="S' N P G R S",
         pakad="S R G, P N S', N P G R", vadi="G", samvadi="P",
         time="evening", rasa="joyful, auspicious",
         aka=["Hansadhwani"]),
    Raga("Jaunpuri", thaat="asavari",
         aroha="S R m P d n S'", avaroha="S' n d P m g R S",
         pakad="m P d n d, P, m P g R S", vadi="d", samvadi="g",
         time="late morning", rasa="pathos, devotion"),
    Raga("Hindol", thaat="kalyan",
         aroha="S G M D N S'", avaroha="S' N D M G S",
         pakad="S G, M D, N D, M G S", vadi="D", samvadi="G",
         time="morning", rasa="joyful, spring", aka=["Hindolam"]),
    Raga("Ahir Bhairav", thaat="bhairav",
         aroha="S r G m P D n S'", avaroha="S' n D P m G r S",
         pakad="S r, G m, D n D, P", vadi="m", samvadi="S",
         time="early morning", rasa="serene, devotional",
         aka=["Ahir Bhairon"]),
    Raga("Jogiya", thaat="bhairav",
         aroha="S r m P d S'", avaroha="S' n d P m r S",
         pakad="m P d, P, m r S", vadi="m", samvadi="S",
         time="early morning", rasa="pathos, renunciation"),
    Raga("Sohni", thaat="marwa",
         aroha="S G M D N S'", avaroha="S' N D M G r S",
         pakad="M D N S', N D M G, M G r S", vadi="D", samvadi="G",
         time="late night", rasa="longing, pathos", aka=["Sohini"]),
    Raga("Puriya", thaat="marwa",
         aroha="N. r G M D N S'", avaroha="S' N D M G r S",
         pakad="N. r G, M G, M D N D M G", vadi="G", samvadi="N",
         time="evening", rasa="serious, contemplative"),
    Raga("Puriya Dhanashri", thaat="purvi",
         aroha="S r G M P d N S'", avaroha="S' N d P M G r S",
         pakad="N. r G, M d, P, M G r G r S", vadi="P", samvadi="r",
         time="sunset", rasa="pathos, devotion",
         aka=["Puriya Dhanashree", "Poorya Dhanashri"]),
    Raga("Shree", thaat="purvi",
         aroha="S r M P N S'", avaroha="S' N d P M G r S",
         pakad="r r S, N. r S, P P, M G r S", vadi="r", samvadi="P",
         time="sunset", rasa="serious, devotional", aka=["Shri", "Sri"]),
    Raga("Multani", thaat="todi",
         aroha="S g M P N S'", avaroha="S' N d P M g r S",
         pakad="N. S g, M g, P g, r S", vadi="P", samvadi="S",
         time="afternoon", rasa="serious, yearning"),
    Raga("Brindabani Sarang", thaat="kafi",
         aroha="S R m P N S'", avaroha="S' n P m R S",
         pakad="N. S R, m R, P m R, n P", vadi="R", samvadi="P",
         time="afternoon", rasa="bright, restful",
         aka=["Vrindavani Sarang", "Brindavani Sarang", "Sarang"]),
    Raga("Megh", thaat="kafi",
         aroha="S R m P n S'", avaroha="S' n P m R S",
         pakad="S R, m R, P, m R n. S", vadi="S", samvadi="P",
         time="monsoon", rasa="monsoon, valour", aka=["Megh Malhar"]),
    Raga("Shivaranjani", thaat="kafi",
         aroha="S R g P D S'", avaroha="S' D P g R S",
         pakad="S R g, P, g R S, D. S", vadi="P", samvadi="R",
         time="night", rasa="pathos, longing",
         aka=["Shivranjani", "Sivaranjani"]),
    Raga("Tilang", thaat="khamaj",
         aroha="S G m P N S'", avaroha="S' n P m G S",
         pakad="S G, m G, P, N S', n P", vadi="G", samvadi="N",
         time="night", rasa="light, romantic", aka=["Tilung"]),
    Raga("Jhinjhoti", thaat="khamaj",
         aroha="S R m P D S'", avaroha="S' n D P m G R S",
         pakad="S R m, P D, m G R, n. S", vadi="G", samvadi="D",
         time="night", rasa="playful, folk", aka=["Jhinjhuti"]),
    Raga("Rageshri", thaat="khamaj",
         aroha="S G m D n S'", avaroha="S' n D m G R S",
         pakad="S G m D, n D, m G R S", vadi="m", samvadi="S",
         time="night", rasa="serene, devotional",
         aka=["Rageshree", "Rageshwari"]),
    Raga("Kalavati", thaat="khamaj",
         aroha="S G P D n S'", avaroha="S' n D P G S",
         pakad="S G P, D n D, P G S", vadi="P", samvadi="G",
         time="night", rasa="sweet, romantic"),
    Raga("Deshkar", thaat="bilawal",
         aroha="S R G P D S'", avaroha="S' D P G R S",
         pakad="D. S R, G P, D P, G R S", vadi="D", samvadi="G",
         time="morning", rasa="bright, expansive"),
    Raga("Shankara", thaat="bilawal",
         aroha="S G P D N S'", avaroha="S' N D P G R S",
         pakad="G P, N S', N D P, G R S", vadi="G", samvadi="N",
         time="late night", rasa="majestic, heroic", aka=["Shankra"]),

    # ── Carnatic ragas ────────────────────────────────────────────────
    # Parent here is the melakarta (the 72-scale system), not a thaat.
    # Carnatic practice doesn't bind ragas to a time of day the way
    # Hindustani does, so `time` is "any".
    Raga("Shankarabharanam", thaat="Dheerashankarabharanam (29)",
         tradition="carnatic",
         aroha="S R G m P D N S'", avaroha="S' N D P m G R S",
         vadi="G", samvadi="N", time="any",
         rasa="majestic, devotional", aka=["Sankarabharanam"]),
    Raga("Kalyani", thaat="Mechakalyani (65)", tradition="carnatic",
         aroha="S R G M P D N S'", avaroha="S' N D P M G R S",
         vadi="G", samvadi="D", time="any",
         rasa="auspicious, grand", aka=["Mechakalyani", "Kalyan"]),
    Raga("Kharaharapriya", thaat="Kharaharapriya (22)", tradition="carnatic",
         aroha="S R g m P D n S'", avaroha="S' n D P m g R S",
         vadi="P", samvadi="S", time="any", rasa="pathos, longing"),
    Raga("Hanumatodi", thaat="Hanumatodi (8)", tradition="carnatic",
         aroha="S r g m P d n S'", avaroha="S' n d P m g r S",
         vadi="d", samvadi="g", time="any", rasa="serious, devotional",
         aka=["Todi (Carnatic)"]),
    Raga("Mayamalavagowla", thaat="Mayamalavagowla (15)",
         tradition="carnatic",
         aroha="S r G m P d N S'", avaroha="S' N d P m G r S",
         vadi="d", samvadi="r", time="any",
         rasa="serious, devotional (the first scale taught)",
         aka=["Malahari parent"]),
    Raga("Mohanam", thaat="Harikambhoji (28)", tradition="carnatic",
         aroha="S R G P D S'", avaroha="S' D P G R S",
         vadi="G", samvadi="D", time="any", rasa="cheerful, devotional"),
    Raga("Hindolam", thaat="Natabhairavi (20)", tradition="carnatic",
         aroha="S g m d n S'", avaroha="S' n d m g S",
         vadi="m", samvadi="S", time="any", rasa="meditative, profound"),
    Raga("Abhogi", thaat="Kharaharapriya (22)", tradition="carnatic",
         aroha="S R g m D S'", avaroha="S' D m g R S",
         vadi="m", samvadi="S", time="any", rasa="pleasing, tender"),
    Raga("Charukesi", thaat="Charukesi (26)", tradition="carnatic",
         aroha="S R G m P d n S'", avaroha="S' n d P m G R S",
         vadi="P", samvadi="S", time="any", rasa="bittersweet"),
    Raga("Keeravani", thaat="Keeravani (21)", tradition="carnatic",
         aroha="S R g m P d N S'", avaroha="S' N d P m g R S",
         vadi="P", samvadi="S", time="any", rasa="romantic, plaintive",
         aka=["Kirwani"]),
    Raga("Natabhairavi", thaat="Natabhairavi (20)", tradition="carnatic",
         aroha="S R g m P d n S'", avaroha="S' n d P m g R S",
         vadi="m", samvadi="S", time="any", rasa="solemn",
         aka=["Asavari equivalent"]),
    Raga("Kambhoji", thaat="Harikambhoji (28)", tradition="carnatic",
         aroha="S R G m P D S'", avaroha="S' n D P m G R S",
         vadi="G", samvadi="P", time="any", rasa="majestic"),
    Raga("Shanmukhapriya", thaat="Shanmukhapriya (56)", tradition="carnatic",
         aroha="S R g M P d n S'", avaroha="S' n d P M g R S",
         vadi="d", samvadi="g", time="any", rasa="intense, yearning"),
    Raga("Simhendramadhyamam", thaat="Simhendramadhyamam (57)",
         tradition="carnatic",
         aroha="S R g M P d N S'", avaroha="S' N d P M g R S",
         vadi="d", samvadi="g", time="any", rasa="grand, serious"),
    Raga("Madhyamavati", thaat="Kharaharapriya (22)", tradition="carnatic",
         aroha="S R m P n S'", avaroha="S' n P m R S",
         vadi="R", samvadi="P", time="any",
         rasa="auspicious (sung to close a concert)"),
    Raga("Bilahari", thaat="Dheerashankarabharanam (29)",
         tradition="carnatic",
         aroha="S R G P D S'", avaroha="S' N D P m G R S",
         vadi="R", samvadi="P", time="any", rasa="joyful, festive"),
    Raga("Saveri", thaat="Mayamalavagowla (15)", tradition="carnatic",
         aroha="S r m P d S'", avaroha="S' N d P m G r S",
         vadi="d", samvadi="r", time="any", rasa="devotional, plaintive"),
    Raga("Shuddha Saveri", thaat="Dheerashankarabharanam (29)",
         tradition="carnatic",
         aroha="S R m P D S'", avaroha="S' D P m R S",
         vadi="m", samvadi="S", time="any", rasa="bright, austere"),
]

_RAGAS = {r.name.lower(): r for r in _RAGA_LIST}
