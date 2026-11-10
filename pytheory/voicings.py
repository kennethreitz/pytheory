"""Search the neck for playable chord voicings in any tuning.

``fingering(..., multiple=True)`` used to keep only the single
best-scoring shape (and, in standard tuning, only the curated grip).
This module searches open position and movable shapes up the neck,
drops anything a hand cannot play, and ranks what remains by one
weighted cost.

The playability checks follow the enumerator dxjqgc wrote while
working on pytheory issue #64 (fork ``dxjqgc/pytheory-fork``; the
search itself is published in
``dxjqgc/rhythm-template-library`` ``chord_fingering``):

* fretted notes span at most four frets
* at most four fretting fingers, with an index barre and short
  partial barres each counting as one finger
* how far two fingers can reach grows as the frets get narrower
* muted strings sit only at the edges of the shape
* a bass note isolated high on the neck is dropped when it only
  duplicates a pitch the rest of the shape already has (the
  "thumb wrap" grip, e.g. ``502220`` for A)
* every chord tone is present; a perfect fifth (and, on dense
  extensions, the eleventh) may be omitted, and that omission is
  part of the cost

Lower cost ranks first. The terms, and why they are weighted this
way, are the module constants below.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations, product
from typing import Optional

from ._statics import C_INDEX

__all__ = [
    "DEFAULT_VOICING_LIMIT",
    "MAX_FRET",
    "MAX_SPAN",
    "FingerPlan",
    "pitch_class",
    "plan_fingers",
    "relative_shape",
    "required_pitch_classes",
    "score_voicing",
    "search_fingerings",
]

# A normal guitar neck, high enough to include E-shape, A-shape, and
# D-shape grips. Fret numbers are semitones above the nut, or above
# the capo when the board was built with one.
MAX_FRET = 15
MAX_SPAN = 4
MAX_FINGERS = 4
# A non-index finger can pinch a short barre (the A chord's D/G/B
# strings). Wider than three strings is an index-finger barre.
MAX_PARTIAL = 3
DEFAULT_VOICING_LIMIT = 8

# --- cost weights (lower total is easier, and ranks first) ----------
#
# Calibrated so textbook open grips beat their barre cousins, a full
# barre beats a heavily muted fragment of the same chord, and an
# omitted fifth is a real but not fatal penalty. Change these only
# with the voicing tests in front of you.

W_FINGER = 0.85          # each fretting finger (a barre is one)
W_INDEX_BARRE = 1.15     # laying the index finger across the neck
W_PARTIAL = 0.90         # a short barre with some other finger
W_SPAN = 0.55            # each fret of stretch between fretted notes
W_LOW_SPAN = 0.20        # extra stretch penalty at the wide low frets
W_MIN_FRET = 0.40        # how far up the neck the grip sits
W_BASS_MUTE = 0.45       # per bass-side mute, applied to the square
W_TREBLE_MUTE = 1.30     # per treble-side mute, applied to the square
W_OPEN = -0.30           # an open string rings and costs no finger
W_SOUNDED = -0.20        # a fuller voicing
W_OMISSION = 1.70        # a missing chord tone (usually the fifth)
W_INVERSION = 2.60       # the lowest sounding pitch is not the root


def pitch_class(tone) -> int:
    """Pitch class 0–11 with C as 0, whether or not *tone* has an octave."""
    if getattr(tone, "octave", None) is not None and tone.midi is not None:
        return tone.midi % 12
    return (tone._index - C_INDEX) % 12


def required_pitch_classes(target: set[int], root_pc: Optional[int]) -> set[int]:
    """Pitch classes a grip must sound.

    Triads, power chords, and altered fifths keep every tone. From a
    seventh onward the perfect fifth may be dropped (it is already in
    the root's overtones), and from a six-note extension the eleventh
    may be dropped too. Both still add :data:`W_OMISSION` to the cost.
    """
    required = set(target)
    if root_pc is None or len(required) < 4:
        return required
    fifth = (root_pc + 7) % 12
    if fifth in required:
        required.remove(fifth)
    if len(target) >= 6:
        required.discard((root_pc + 5) % 12)
    return required


def relative_shape(positions: Sequence[Optional[int]]) -> tuple:
    """Identity of a grip, ignoring where it sits on the neck.

    Open strings stay open and mutes stay muted, so an open C and the
    A-shape barre C do not collapse into each other. Two barres of the
    same shape at different frets do.
    """
    fretted = [p for p in positions if p]
    base = min(fretted) if fretted else 0
    out = []
    for p in positions:
        if p is None:
            out.append(None)
        elif p == 0:
            out.append("open")
        else:
            out.append(p - base)
    return tuple(out)


@dataclass(frozen=True)
class FingerPlan:
    """One way to put the fretting hand on a shape.

    ``n_fingers`` counts a barre as a single finger. ``min_fret`` is 0
    when every sounding string is open.
    """

    n_fingers: int
    index_barre: bool
    n_partial: int
    span: int
    min_fret: int

    @property
    def hand_cost(self) -> float:
        cost = self.n_fingers * W_FINGER
        if self.index_barre:
            cost += W_INDEX_BARRE
        cost += self.n_partial * W_PARTIAL
        cost += self.span * W_SPAN
        if self.min_fret <= 2:
            cost += self.span * W_LOW_SPAN
        cost += self.min_fret * W_MIN_FRET
        return cost


@dataclass(frozen=True)
class _Unit:
    fret: int
    lo: int
    hi: int
    index_barre: bool
    partial: bool


def _reach(base_fret: int) -> float:
    """Frets one finger-step can cover. Frets get narrower up the neck."""
    if base_fret <= 2:
        return 1.0
    if base_fret <= 5:
        return 4 / 3
    if base_fret <= 9:
        return 5 / 3
    return 2.0


def _runs(strings: Sequence[int]) -> list[tuple[int, int]]:
    ordered = sorted(strings)
    runs: list[tuple[int, int]] = []
    start = prev = ordered[0]
    for s in ordered[1:]:
        if s == prev + 1:
            prev = s
        else:
            runs.append((start, prev))
            start = prev = s
    runs.append((start, prev))
    return runs


def _index_barre_range(positions: Sequence[Optional[int]]):
    """Contiguous index-finger barre at the lowest fretted fret, if any.

    Every string between the outermost notes on that fret has to be
    held at that fret or higher. An open string or a mute in the
    middle breaks the barre (the open G chord's two notes at fret 3
    are not a barre).
    """
    fretted = [(i, p) for i, p in enumerate(positions) if p]
    if not fretted:
        return None
    bf = min(p for _, p in fretted)
    at = [i for i, p in fretted if p == bf]
    if len(at) < 2:
        return None
    lo, hi = min(at), max(at)
    for i in range(lo, hi + 1):
        p = positions[i]
        if p is None or p == 0 or p < bf:
            return None
    return lo, hi, bf


def _partitions(positions: Sequence[Optional[int]], use_index_barre: bool):
    fretted = {i: p for i, p in enumerate(positions) if p}
    if not fretted:
        return [[]]
    if use_index_barre:
        rng = _index_barre_range(positions)
        if rng is None:
            return []
        lo, hi, bf = rng
        fixed = [_Unit(bf, lo, hi, True, False)]
        rest = {i: p for i, p in fretted.items() if p > bf}
    else:
        fixed = []
        rest = dict(fretted)

    by_fret: dict[int, list[int]] = {}
    for i, p in rest.items():
        by_fret.setdefault(p, []).append(i)

    choices: list[list[list[_Unit]]] = []
    for fret, strings in by_fret.items():
        for lo, hi in _runs(strings):
            width = hi - lo + 1
            singles = [
                _Unit(fret, s, s, False, False) for s in range(lo, hi + 1)
            ]
            if 1 < width <= MAX_PARTIAL:
                choices.append([
                    singles,
                    [_Unit(fret, lo, hi, False, True)],
                ])
            else:
                choices.append([singles])

    if not choices:
        return [fixed]
    return [
        fixed + [u for group in combo for u in group]
        for combo in product(*choices)
    ]


def _fingers_cross(units: Sequence[_Unit], positions: Sequence[Optional[int]]) -> bool:
    """Two non-barre fingers on one fret cannot straddle a higher fret.

    Adjacent fingers, or fingers with only an open string between them,
    are fine — that is how the open G is played. A higher fret between
    them means one finger would have to reach around the other.
    """
    ordered = sorted(units, key=lambda u: u.lo)
    for a, b in combinations(ordered, 2):
        # An index barre is allowed to sit under higher fingers. A
        # partial barre is an ordinary finger and cannot.
        if a.fret != b.fret or a.index_barre or b.index_barre:
            continue
        if b.lo - a.hi - 1 < 2:
            continue
        for s in range(a.hi + 1, b.lo):
            p = positions[s]
            if p is not None and p > a.fret:
                return True
    return False


def _assignable(units: Sequence[_Unit], base_fret: int) -> bool:
    """Can these finger-units be worn by four fingers without crossing?

    An index barre, when present, has to be finger 1. Higher frets get
    higher finger numbers, and the fret gap between two fingers cannot
    exceed their finger gap times :func:`_reach`.
    """
    if len(units) > MAX_FINGERS:
        return False
    if not units:
        return True
    ordered = sorted(units, key=lambda u: (u.fret, u.lo))
    barre_at = next((i for i, u in enumerate(ordered) if u.index_barre), None)
    reach = _reach(base_fret)
    k = len(ordered)
    for fingers in combinations(range(1, MAX_FINGERS + 1), k):
        if barre_at is not None and fingers[barre_at] != 1:
            continue
        if all(
            ordered[j].fret - ordered[i].fret
            <= (fingers[j] - fingers[i]) * reach + 1e-9
            for i in range(k)
            for j in range(i + 1, k)
        ):
            return True
    return False


def plan_fingers(positions: Sequence[Optional[int]]) -> Optional[FingerPlan]:
    """Cheapest playable finger plan, or ``None`` when the shape is not.

    *positions* are in string order (either orientation). ``None`` is a
    mute, ``0`` an open string, and any other integer a fret.
    """
    fretted = [p for p in positions if p]
    if not fretted:
        if any(p is not None for p in positions):
            return FingerPlan(0, False, 0, 0, 0)
        return None
    span = max(fretted) - min(fretted)
    if span > MAX_SPAN:
        return None
    base = min(fretted)

    best: Optional[FingerPlan] = None
    for use_barre in (False, True):
        for units in _partitions(positions, use_barre):
            if _fingers_cross(units, positions):
                continue
            if not _assignable(units, base):
                continue
            plan = FingerPlan(
                n_fingers=len(units),
                index_barre=any(u.index_barre for u in units),
                n_partial=sum(1 for u in units if u.partial),
                span=span,
                min_fret=base,
            )
            if best is None or plan.hand_cost < best.hand_cost:
                best = plan
    return best


def _mute_limits(n_strings: int) -> tuple[int, int, int]:
    """(max bass mutes, max treble mutes, max sounding strings).

    On a guitar the low D chord mutes two bass strings and nothing on
    top, so those are the caps. Larger instruments keep a window of at
    most six sounding strings — a hand does not fret more than that
    independently — placed anywhere across the course.
    """
    if n_strings <= 4:
        return (1 if n_strings >= 4 else 0), 0, n_strings
    if n_strings == 5:
        return 2, 1, 5
    if n_strings == 6:
        return 2, 1, 6
    return n_strings - 3, n_strings - 3, 6


def _interior_open(positions: Sequence[Optional[int]], first_position: int = MAX_SPAN) -> bool:
    """An open string trapped between fretted notes above first position.

    Open strings inside a first-position grip are normal (the open G).
    The same hole under a grip at the 5th fret and higher is a drone
    in the middle of the hand, which this search does not treat as a
    separate voicing. Bass drones — opens on the bass side of every
    fretted note — are not interior.
    """
    fretted_idx = [i for i, p in enumerate(positions) if p]
    if len(fretted_idx) < 2:
        return False
    if min(p for p in positions if p) <= first_position:
        return False
    lo, hi = min(fretted_idx), max(fretted_idx)
    return any(positions[i] == 0 for i in range(lo + 1, hi))


def _root_in_bass(positions, open_tones, root_pc) -> bool:
    sounding = [(i, p) for i, p in enumerate(positions) if p is not None]
    if not sounding or root_pc is None:
        return False
    i, p = min(sounding, key=lambda ip: open_tones[ip[0]].midi + ip[1])
    return (open_tones[i].midi + p) % 12 == root_pc


def _redundant_thinning(thinner, fuller, pc_at, open_tones, root_pc) -> bool:
    """True when *thinner* is *fuller* with doubled edge notes muted.

    ``32000x`` is the open G with the top string skipped, so it does
    not earn its own place. The small F (``xx3211``) mutes two strings
    of the barre and is still a four-note root-position grip, so it
    stays. A one-string trim never stays: it is the same hand.
    """
    if len(thinner) != len(fuller):
        return False
    extra = []
    for i, (a, b) in enumerate(zip(thinner, fuller)):
        if a == b:
            continue
        if a is not None or b is None:
            return False
        extra.append(i)
    if not extra:
        return False
    present = {pc_at(j, p) for j, p in enumerate(thinner) if p is not None}
    if any(pc_at(i, fuller[i]) not in present for i in extra):
        return False
    n_sound = sum(p is not None for p in thinner)
    # One muted string is the same grip. Two or more can be a real
    # smaller chord (the small F) when the root is still in the bass
    # and four strings are still sounding.
    if len(extra) >= 2 and n_sound >= 4 and _root_in_bass(thinner, open_tones, root_pc):
        return False
    return True


def _edge_mutes(positions: Sequence[Optional[int]]) -> tuple[int, int]:
    """(bass-side mutes, treble-side mutes) for a canonical shape.

    Canonical order is high string first, so the treble edge is the
    start of the tuple and the bass edge is the end.
    """
    sounding = [i for i, p in enumerate(positions) if p is not None]
    if not sounding:
        return 0, 0
    treble = sounding[0]
    bass = len(positions) - 1 - sounding[-1]
    return bass, treble


def _redundant_thumb(positions, pcs_at, required: set[int]) -> bool:
    """True when the bass-most fretted note is an isolated duplicate.

    ``502220`` puts the low E at fret 5 for a low A that the open A
    string already sounds, and the gap below the rest of the grip is
    a thumb wrap. Dropping that note still leaves an A major, so the
    shape is the ordinary ``x02220`` with an unplayable extra.
    """
    fretted = [(i, p) for i, p in enumerate(positions) if p]
    if len(fretted) < 2:
        return False
    bass_i, bass_f = max(fretted)  # canonical order: the last string is the bass
    # The next fretted string toward the treble is what the hand reaches from.
    neighbor_f = min(
        (item for item in fretted if item[0] < bass_i),
        key=lambda item: bass_i - item[0],
    )[1]
    if bass_f <= neighbor_f + 2:
        return False
    present = {
        pcs_at(i, p)
        for i, p in enumerate(positions)
        if p is not None and i != bass_i
    }
    return required <= present


def score_voicing(positions, open_tones, *, target_pcs: set[int],
                  root_pc: Optional[int], plan: Optional[FingerPlan] = None) -> float:
    """Cost of one canonical shape. Lower is easier. Unplayable is infinite.

    Cost =
    hand (fingers, barres, stretch, fret height)
    + bass mutes² × :data:`W_BASS_MUTE`
    + treble mutes² × :data:`W_TREBLE_MUTE`
    + omitted chord tones × :data:`W_OMISSION`
    + :data:`W_INVERSION` when the lowest pitch is not the root
    + open strings × :data:`W_OPEN`
    + sounding strings × :data:`W_SOUNDED`
    """
    if plan is None:
        plan = plan_fingers(positions)
    if plan is None:
        return float("inf")

    sounding = [
        (i, p) for i, p in enumerate(positions) if p is not None
    ]
    if not sounding:
        return float("inf")
    pcs = {(open_tones[i].midi + p) % 12 for i, p in sounding}
    if not pcs <= target_pcs:
        return float("inf")
    required = required_pitch_classes(target_pcs, root_pc)
    if not required <= pcs:
        return float("inf")

    bass_mutes, treble_mutes = _edge_mutes(positions)
    # An interior mute never reaches here through the search; reject
    # it if a caller scores one directly.
    if bass_mutes + treble_mutes != sum(1 for p in positions if p is None):
        return float("inf")

    n_open = sum(1 for _, p in sounding if p == 0)
    omitted = len(target_pcs - pcs)
    cost = plan.hand_cost
    cost += bass_mutes ** 2 * W_BASS_MUTE
    cost += treble_mutes ** 2 * W_TREBLE_MUTE
    cost += omitted * W_OMISSION
    cost += n_open * W_OPEN
    cost += len(sounding) * W_SOUNDED

    if root_pc is not None:
        lowest = min(sounding, key=lambda ip: open_tones[ip[0]].midi + ip[1])
        if (open_tones[lowest[0]].midi + lowest[1]) % 12 != root_pc:
            cost += W_INVERSION
    return cost


def _min_sounding(n_strings: int, n_required: int) -> int:
    floor = 3 if n_strings >= 5 else 2
    return min(n_strings, max(n_required, floor))


def search_fingerings(open_tones, target_pcs: set[int], *,
                      root_pc: Optional[int],
                      max_fret: int = MAX_FRET,
                      max_span: int = MAX_SPAN) -> list[tuple]:
    """Canonical fret tuples (high string first, ``None`` = mute), best first.

    Each returned shape is a different grip: the same barre slid up
    the neck is kept once, at whichever fret is easiest. *open_tones*
    are the board's canonical (high-to-low) open strings.
    """
    tones = list(open_tones)
    n = len(tones)
    if n == 0 or not target_pcs:
        return []
    target = set(target_pcs)
    required = required_pitch_classes(target, root_pc)
    options = [
        [f for f in range(max_fret + 1) if (tone.midi + f) % 12 in target]
        for tone in tones
    ]

    def pc_at(i, fret):
        return (tones[i].midi + fret) % 12

    max_bass, max_treble, max_sounding = _mute_limits(n)
    min_sounding = _min_sounding(n, len(required))
    seen: set[tuple] = set()
    best: dict[tuple, tuple] = {}

    def consider(key: tuple) -> None:
        if key in seen or _interior_open(key):
            return
        seen.add(key)
        present = {pc_at(i, p) for i, p in enumerate(key) if p is not None}
        if not required <= present:
            return
        if _redundant_thumb(key, pc_at, required):
            return
        plan = plan_fingers(key)
        if plan is None:
            return
        cost = score_voicing(
            key, tones, target_pcs=target, root_pc=root_pc, plan=plan,
        )
        if cost == float("inf"):
            return
        shape = relative_shape(key)
        prev = best.get(shape)
        # None (a mute) has to sort; it is not an int.
        order = tuple(-1 if p is None else p for p in key)
        rank = (cost, plan.min_fret, order)
        if prev is None or rank < prev[0]:
            best[shape] = (rank, key)

    def products(indexes, lists):
        size = 1
        for c in lists:
            size *= len(c)
            if size > 8000:
                return
        for combo in product(*lists):
            positions = [None] * n
            for idx, fret in zip(indexes, combo):
                positions[idx] = fret
            consider(tuple(positions))

    for n_treble in range(max_treble + 1):
        for n_bass in range(max_bass + 1):
            n_sound = n - n_treble - n_bass
            if n_sound < min_sounding or n_sound > max_sounding or n_sound <= 0:
                continue
            sounding_idx = list(range(n_treble, n - n_bass))
            for base in range(0, max_fret - max_span + 1):
                cands = []
                ok = True
                for i in sounding_idx:
                    window = [
                        f for f in options[i]
                        if base <= f <= base + max_span
                    ]
                    # Open strings belong to first-position grips.
                    if base <= max_span and 0 in options[i] and 0 not in window:
                        window.append(0)
                    if not window:
                        ok = False
                        break
                    cands.append(window)
                if ok:
                    products(sounding_idx, cands)

                # Bass drones under a movable grip: the lowest one or
                # two sounding strings ring open, the rest sit in the
                # window. No open string is left in the middle.
                if base <= max_span:
                    continue
                for n_drone in (1, 2):
                    if n_drone >= n_sound:
                        continue
                    drone_idx = sounding_idx[-n_drone:]
                    fretted_idx = sounding_idx[:-n_drone]
                    if any(0 not in options[i] for i in drone_idx):
                        continue
                    fretted_cands = []
                    ok = True
                    for i in fretted_idx:
                        window = [
                            f for f in options[i]
                            if base <= f <= base + max_span and f != 0
                        ]
                        if not window:
                            ok = False
                            break
                        fretted_cands.append(window)
                    if not ok:
                        continue
                    products(
                        fretted_idx + drone_idx,
                        fretted_cands + [[0] for _ in drone_idx],
                    )

    ranked = [key for _, key in sorted(best.values(), key=lambda item: item[0])]
    kept: list[tuple] = []
    for key in ranked:
        if any(_redundant_thinning(key, prev, pc_at, tones, root_pc) for prev in kept):
            continue
        kept.append(key)
    return kept
