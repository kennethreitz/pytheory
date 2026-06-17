"""SVG fretboard diagrams — chord charts, scale shapes, arpeggio maps.

ASCII tabs are perfect in a terminal, but you can't drop them into a
video, a slide, or a worksheet. This module renders the same fretboard
data as clean, scalable SVG you can embed anywhere.

Three things are exposed (all reachable from :class:`~pytheory.Fretboard`
and :class:`~pytheory.charts.Fingering`):

- **chord diagrams** — the vertical chord box you see in songbooks,
  with open/muted markers and automatic barre detection.
- **scale shapes** — a scale split into positional boxes (e.g. the five
  pentatonic positions), each a small fret window with the roots marked.
- **arpeggio diagrams** — every chord tone across the neck, labelled by
  its role (R, 3, 5, 7…) so you can practise where the notes live.

SVG is pure text, so there are no dependencies. To rasterize to PNG,
pass ``fmt="png"`` (needs the optional ``cairosvg`` package).

Example::

    >>> from pytheory import Fretboard
    >>> Fretboard.guitar().tab_image("Am", path="Am.svg")
    >>> for name in ["C", "Am", "F", "G"]:
    ...     Fretboard.guitar().tab_image(name, path=f"{name}.svg")
"""
from __future__ import annotations

# ── palette ──────────────────────────────────────────────────────────
_INK = "#222222"
_DOT = "#222222"
_ROOT = "#c0392b"        # roots stand out in red
_MUTE = "#999999"
_PAPER = "#ffffff"
_FONT = ("font-family=\"-apple-system, Helvetica, Arial, sans-serif\"")


def _svg(width: float, height: float, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width:g}" height="{height:g}" '
        f'viewBox="0 0 {width:g} {height:g}">'
        f'<rect width="{width:g}" height="{height:g}" fill="{_PAPER}"/>'
        f'{body}</svg>'
    )


def _line(x1, y1, x2, y2, w=1.5, color=_INK):
    return (f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" '
            f'stroke="{color}" stroke-width="{w:g}" stroke-linecap="round"/>')


def _text(x, y, s, size=13, color=_INK, weight="normal", anchor="middle"):
    return (f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" {_FONT} '
            f'fill="{color}" font-weight="{weight}" '
            f'text-anchor="{anchor}" dominant-baseline="middle">{s}</text>')


def _dot(x, y, r, fill=_DOT, label=None, label_color="#ffffff"):
    out = f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="{fill}"/>'
    if label:
        out += _text(x, y, label, size=r, color=label_color, weight="bold")
    return out


def _ring(x, y, r):
    return (f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="none" '
            f'stroke="{_INK}" stroke-width="1.5"/>')


def _maybe_write(svg: str, path, fmt: str):
    """Write to *path* (rasterizing to PNG if asked) or return the SVG."""
    if fmt == "png" or (path and str(path).lower().endswith(".png")):
        try:
            import cairosvg
        except ImportError:
            raise ImportError(
                "PNG export needs the 'cairosvg' package "
                "(pip install cairosvg). SVG export has no dependencies.")
        data = cairosvg.svg2png(bytestring=svg.encode("utf-8"))
        if path:
            with open(path, "wb") as f:
                f.write(data)
            return path
        return data
    if path:
        with open(path, "w") as f:
            f.write(svg)
        return path
    return svg


# ── chord box ────────────────────────────────────────────────────────

def chord_svg(fingering, name=None, *, path=None, fmt="svg",
              cell: float = 30.0) -> str:
    """Render a :class:`Fingering` as a vertical chord-box SVG.

    Args:
        fingering: a :class:`~pytheory.charts.Fingering`.
        name: title above the box (defaults to the identified chord name).
        path: if given, write the file and return the path.
        fmt: ``"svg"`` (default) or ``"png"`` (needs ``cairosvg``).
        cell: grid spacing in pixels.
    """
    names = list(fingering.string_names)     # low → high (left → right)
    frets = list(fingering.positions)
    n = len(names)

    fretted = [f for f in frets if f not in (None, 0)]
    if fretted:
        lo, hi = min(fretted), max(fretted)
    else:
        lo = hi = 0
    # Show the nut when the shape sits low on the neck; otherwise show a
    # window starting at the lowest fretted note and label its position.
    if not fretted or hi <= 4:
        base, rows, show_nut = 0, max(4, hi), True
    else:
        base, rows, show_nut = lo - 1, max(4, hi - lo + 2), False

    pad_x, top = 22.0, 46.0
    width = pad_x * 2 + (n - 1) * cell
    height = top + rows * cell + 26
    x = lambda i: pad_x + i * cell
    y = lambda f: top + f * cell

    body = []
    if name is None:
        name = fingering.identify() or ""
    if name:
        body.append(_text(width / 2, 18, name, size=17, weight="bold"))

    # Work out the root pitch class (to highlight) and each string's
    # sounding pitch class, when a fretboard is attached.
    # Pull just the root note out of the label — a name like "Cadd9" or
    # "F#m7b5" isn't a tone, so feeding the whole thing to _pc() would crash.
    ident = fingering.identify() or name
    root_pc = None
    if ident:
        import re
        m = re.match(r"\s*([A-Ga-g][#b]*)", ident)
        if m:
            try:
                root_pc = _pc(m.group(1))
            except ValueError:
                root_pc = None
    string_pcs = [None] * n
    if fingering._fretboard is not None:
        opens = fingering._orient(fingering._fretboard._tones)
        for i, f in enumerate(frets):
            if f is not None and i < len(opens):
                string_pcs[i] = (opens[i].midi + f) % 12

    # Grid: fret wires and strings.
    for f in range(rows + 1):
        w = 5.0 if (f == 0 and show_nut) else 1.5
        body.append(_line(x(0), y(f), x(n - 1), y(f), w=w))
    for i in range(n):
        body.append(_line(x(i), y(0), x(i), y(rows)))

    if not show_nut:
        body.append(_text(x(0) - 14, y(0) + cell / 2, f"{base + 1}fr",
                          size=12, anchor="middle"))

    # Barre: the lowest fretted fret shared by 2+ strings draws a bar.
    if fretted:
        barre_fret = lo
        cols = [i for i, f in enumerate(frets) if f == barre_fret]
        if len(cols) >= 2:
            yc = y(barre_fret - base - 0.5)
            body.append(
                f'<rect x="{x(cols[0]) - cell * 0.32:g}" '
                f'y="{yc - cell * 0.32:g}" '
                f'width="{x(cols[-1]) - x(cols[0]) + cell * 0.64:g}" '
                f'height="{cell * 0.64:g}" rx="{cell * 0.32:g}" '
                f'fill="{_DOT}"/>')

    # Markers above the nut and dots on the board.
    r = cell * 0.30
    for i, f in enumerate(frets):
        if f is None:
            body.append(_text(x(i), y(0) - 14, "✕", size=14, color=_MUTE))
        elif f == 0:
            is_root = root_pc is not None and string_pcs[i] == root_pc
            body.append(_ring(x(i), y(0) - 14, r * 0.8))
            if is_root:   # mark an open root with a filled ring
                body.append(_dot(x(i), y(0) - 14, r * 0.5, fill=_ROOT))
        else:
            is_root = root_pc is not None and string_pcs[i] == root_pc
            body.append(_dot(x(i), y(f - base - 0.5), r,
                            fill=_ROOT if is_root else _DOT))

    return _maybe_write(_svg(width, height, "".join(body)), path, fmt)


# ── horizontal neck (scale shapes & arpeggios) ───────────────────────

_INLAYS = {3, 5, 7, 9, 15, 17, 19, 21}
_DOUBLE_INLAYS = {12, 24}


def _neck_svg(string_labels, rows, lo, hi, dots, *, title=None,
              cell: float = 34.0):
    """Render a horizontal neck window spanning frets ``lo``..``hi``.

    Frets ``lo``..``hi`` each get a cell. When ``lo == 0`` the left edge
    is the nut and open strings (fret 0) are drawn as rings beside it;
    otherwise it's a movable position window starting at fret ``lo``.

    Args:
        string_labels: open-string names, top → bottom (high → low).
        rows: number of strings.
        lo, hi: lowest and highest fret shown.
        dots: list of ``(string_row, fret, label, is_root)``.
        title: optional heading.
    """
    nut = lo == 0
    first = 1 if nut else lo            # first fret that gets a cell
    cells = hi - first + 1
    pad_l, pad_top, pad_r, pad_bot = 54.0, 34.0, 18.0, 26.0
    width = pad_l + cells * cell + pad_r
    height = pad_top + (rows - 1) * cell + pad_bot
    # Left border sits at the boundary before `first`.
    bx = lambda k: pad_l + k * cell                    # x of the k-th wire
    cx = lambda f: pad_l + (f - first + 0.5) * cell     # x of a note at fret f
    ry = lambda s: pad_top + s * cell                  # y of a string

    body = []
    if title:
        body.append(_text(width / 2, 14, title, size=15, weight="bold"))

    # Inlay markers (faint), drawn behind the grid.
    for f in range(first, hi + 1):
        if f in _DOUBLE_INLAYS:
            for s in (0.5, rows - 1.5):
                body.append(_dot(cx(f), ry(s), 4, fill="#e6e6e6"))
        elif f in _INLAYS:
            body.append(_dot(cx(f), ry((rows - 1) / 2), 4, fill="#e6e6e6"))

    # Strings (horizontal) and frets (vertical).
    for s in range(rows):
        body.append(_line(bx(0), ry(s), bx(cells), ry(s)))
    for k in range(cells + 1):
        w = 5.0 if (nut and k == 0) else 1.5
        body.append(_line(bx(k), ry(0), bx(k), ry(rows - 1), w=w))

    # String names far left, then a column for open-string markers.
    for s, label in enumerate(string_labels):
        body.append(_text(14, ry(s), label, size=12, color=_MUTE))
    for f in range(first, hi + 1):
        body.append(_text(cx(f), ry(rows - 1) + 18, str(f),
                         size=11, color=_MUTE))

    # Notes.
    r = cell * 0.34
    for (s, f, label, is_root) in dots:
        if f == 0:                       # open string — marker off the nut
            ox = bx(0) - 18
            if is_root:
                body.append(_dot(ox, ry(s), r * 0.8, fill=_ROOT, label=label))
            else:
                body.append(_ring(ox, ry(s), r * 0.8))
                if label:
                    body.append(_text(ox, ry(s), label, size=r * 0.72,
                                     color=_INK, weight="bold"))
        else:
            body.append(_dot(cx(f), ry(s), r,
                            fill=_ROOT if is_root else _DOT, label=label))

    return _svg(width, height, "".join(body))


# ── pitch helpers ────────────────────────────────────────────────────

def _pc(name: str) -> int:
    from .tones import Tone
    return Tone.from_string(f"{name}4", system="western").midi % 12


_INTERVAL_LABELS = {
    0: "R", 1: "b9", 2: "9", 3: "b3", 4: "3", 5: "11", 6: "b5",
    7: "5", 8: "b6", 9: "6", 10: "b7", 11: "7",
}


# ── scale shapes (positional boxes) ──────────────────────────────────

class ScaleShape:
    """One positional box of a scale on the fretboard.

    Attributes:
        index: position number (1-based).
        base: lowest fret shown (0 = nut).
        span: number of frets the box spans.
        root_name: the scale's tonic.
        notes: ``(string_row, fret, note_name, is_root)`` tuples, where
            ``string_row`` 0 is the highest-pitched string.
        string_labels: open-string names, high → low.
    """

    def __init__(self, index, base, span, root_name, notes, string_labels):
        self.index = index
        self.base = base
        self.span = span
        self.root_name = root_name
        self.notes = notes
        self.string_labels = string_labels

    @property
    def fret_range(self) -> tuple[int, int]:
        """The (lowest, highest) fret this box covers."""
        return (self.base, self.base + self.span)

    def __repr__(self):
        lo, hi = self.fret_range
        return (f"<ScaleShape {self.root_name} pos {self.index} "
                f"frets {lo}-{hi}>")

    def to_svg(self, *, path=None, fmt="svg", labels="note"):
        """Render this box as SVG (see :func:`scale_shape_svg`)."""
        title = f"{self.root_name}  ·  position {self.index}  ({self.base}-{self.base + self.span}fr)"
        dots = []
        for (s, f, name, is_root) in self.notes:
            if labels == "none":
                text = None
            elif labels == "degree":
                text = "R" if is_root else ""
            else:
                text = name
            dots.append((s, f, text, is_root))
        svg = _neck_svg(self.string_labels, len(self.string_labels),
                        self.base, self.base + self.span, dots, title=title)
        return _maybe_write(svg, path, fmt)


def scale_shapes(fretboard, scale, *, root=None, span=None, max_fret=12):
    """Split a scale into positional boxes across the neck.

    Each box is a small fret window (one comfortable hand position) with
    the scale's notes that fall inside it and the roots marked. For a
    pentatonic scale this yields the familiar five positions.

    Args:
        fretboard: the :class:`~pytheory.Fretboard` to map onto.
        scale: anything with a ``note_names`` list (a Scale, TonedScale
            mode, etc.).
        root: the tonic to treat as the root (defaults to the scale's
            first note).
        span: frets per box (defaults to 3 for pentatonic scales, 4 for
            larger scales — a one-finger-per-fret hand span).
        max_fret: highest fret to anchor boxes within (default 12).

    Returns:
        A list of :class:`ScaleShape`, one per position, low to high.
    """
    canonical = list(fretboard._tones)          # high → low
    string_labels = [t.name for t in canonical]
    pcs = {_pc(n) for n in scale.note_names}
    root_name = root or scale.note_names[0]
    root_pc = _pc(root_name)

    # Pentatonic boxes hold two notes per string, diatonic ones three.
    # The boxes are slanted, so a flat window would clip them — instead
    # take a generous window and keep the lowest N notes on each string,
    # which follows the slant and connects box to box.
    nps = 2 if len(pcs) <= 5 else 3
    window = span if span is not None else nps + 2

    lowest = canonical[-1]
    # Anchor a box at each scale tone on the lowest string within an
    # octave — these are the distinct positions.
    anchors = [f for f in range(0, 12)
               if (lowest.add(f).midi % 12) in pcs]

    shapes = []
    for i, start in enumerate(anchors, start=1):
        if start > max_fret:
            break
        notes = []
        for s, open_tone in enumerate(canonical):
            found = []
            for f in range(start, start + window + 1):
                t = open_tone.add(f)
                if (t.midi % 12) in pcs:
                    found.append((s, f, t.name, (t.midi % 12) == root_pc))
                if len(found) >= nps:
                    break
            notes.extend(found)
        # Crop the drawn window to the notes actually in the box.
        frets = [f for (_, f, _, _) in notes]
        base = min(frets)
        shown = max(3, max(frets) - base)
        shapes.append(
            ScaleShape(i, base, shown, root_name, notes, string_labels))
    return shapes


def scale_shape_svg(fretboard, scale, position, **kw):
    """Render a single scale position. ``position`` is 1-based."""
    shapes = scale_shapes(fretboard, scale)
    if not 1 <= position <= len(shapes):
        raise ValueError(
            f"position {position} out of range (1-{len(shapes)})")
    return shapes[position - 1].to_svg(**kw)


# ── arpeggio diagram (chord tones across the neck) ───────────────────

def arpeggio_svg(fretboard, chord, *, root=None, max_fret=12,
                 path=None, fmt="svg", labels="degree"):
    """Map a chord's tones across the whole neck, labelled by role.

    Shows every place the chord's tones (root, 3rd, 5th, 7th…) fall on
    the fretboard up to ``max_fret``, with roots highlighted — for
    practising arpeggios and seeing where the chord tones live.

    Args:
        fretboard: the :class:`~pytheory.Fretboard`.
        chord: a :class:`~pytheory.Chord` (or chord-symbol string).
        root: override the root (defaults to the chord's lowest tone).
        max_fret: highest fret to show (default 12).
        labels: ``"degree"`` (R/3/5/7…), ``"note"`` (names), or ``"none"``.
    """
    from .chords import Chord
    if isinstance(chord, str):
        chord = Chord.from_symbol(chord)

    canonical = list(fretboard._tones)
    string_labels = [t.name for t in canonical]
    root_pc = _pc(root) if root else (chord.tones[0].midi % 12)
    members = {t.midi % 12 for t in chord.tones}

    title_name = chord.identify() or "arpeggio"

    dots = []
    for s, open_tone in enumerate(canonical):
        for f in range(0, max_fret + 1):
            pc = open_tone.add(f).midi % 12
            if pc in members:
                is_root = pc == root_pc
                if labels == "none":
                    text = None
                elif labels == "note":
                    text = open_tone.add(f).name
                else:
                    text = _INTERVAL_LABELS.get((pc - root_pc) % 12, "")
                dots.append((s, f, text, is_root))

    svg = _neck_svg(string_labels, len(canonical), 0, max_fret, dots,
                    title=f"{title_name}  ·  arpeggio")
    return _maybe_write(svg, path, fmt)
# (arpeggio spans the whole neck, frets 0..max_fret)
