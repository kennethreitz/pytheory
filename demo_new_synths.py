"""Demo the 5 new synths: Mellotron, Hard Sync, Ring Mod, Wavefold, Drift.

Each synth gets a short musical phrase — not just a scale run — with
reverb and rhythmic variety to show off its character.
"""
from pytheory import Score, Duration, play_score

EIGHTH = Duration.EIGHTH
QUARTER = Duration.QUARTER
HALF = Duration.HALF
DOTTED_Q = Duration.DOTTED_QUARTER
WHOLE = Duration.WHOLE


# ── Mellotron Strings ────────────────────────────────────────────────────────
# Strawberry Fields vibes — slow, haunted, with rests that breathe.

print("=== MELLOTRON STRINGS ===")
s = Score("4/4", bpm=72)
p = s.part("tape", instrument="mellotron_strings",
           reverb=0.45, reverb_type="cathedral", reverb_decay=2.0)
p.add("G4", HALF).add("B4", QUARTER).add("D5", QUARTER)
p.add("C5", DOTTED_Q).add("B4", EIGHTH).add("A4", HALF)
p.rest(QUARTER)
p.add("G4", DOTTED_Q).add("F#4", EIGHTH).add("G4", WHOLE)
play_score(s)


# ── Mellotron Flute ──────────────────────────────────────────────────────────
# Lonely, breathy, with space between phrases.

print("\n=== MELLOTRON FLUTE ===")
s = Score("3/4", bpm=84)
p = s.part("flute", instrument="mellotron_flute",
           reverb=0.5, reverb_type="taj_mahal", reverb_decay=2.5)
p.add("E5", HALF).add("D5", QUARTER)
p.add("C5", DOTTED_Q).add("B4", EIGHTH).rest(QUARTER)
p.add("A4", HALF).add("G4", QUARTER)
p.add("A4", HALF).rest(QUARTER)
p.add("E5", QUARTER).add("D5", QUARTER).add("C5", QUARTER)
p.add("B4", HALF + QUARTER)
play_score(s)


# ── Mellotron Choir ──────────────────────────────────────────────────────────
# Ghostly pad — slow chords, big reverb.

print("\n=== MELLOTRON CHOIR ===")
s = Score("4/4", bpm=60)
p = s.part("choir", instrument="mellotron_choir",
           reverb=0.6, reverb_type="cathedral", reverb_decay=3.0)
p.add("C4", WHOLE)
p.add("E4", HALF).add("G4", HALF)
p.add("A4", DOTTED_Q).add("G4", EIGHTH).add("F4", HALF)
p.add("E4", WHOLE)
play_score(s)


# ── Hard Sync Lead ───────────────────────────────────────────────────────────
# Aggressive, punchy — fast 16ths and syncopation.

print("\n=== HARD SYNC LEAD ===")
s = Score("4/4", bpm=128)
p = s.part("sync", instrument="sync_lead",
           reverb=0.25, reverb_type="plate")
p.add("E4", EIGHTH).add("E4", EIGHTH).rest(EIGHTH).add("G4", EIGHTH)
p.add("A4", QUARTER).add("G4", EIGHTH).add("E4", EIGHTH)
p.add("D4", EIGHTH).rest(EIGHTH).add("E4", EIGHTH).add("G4", EIGHTH)
p.add("A4", HALF)
p.rest(QUARTER).add("B4", EIGHTH).add("A4", EIGHTH)
p.add("G4", QUARTER).add("E4", QUARTER).add("D4", HALF)
play_score(s)


# ── Hard Sync Bright ─────────────────────────────────────────────────────────
# Higher slave ratio — more harmonics, screaming lead.

print("\n=== HARD SYNC BRIGHT ===")
s = Score("4/4", bpm=138)
p = s.part("sync2", instrument="sync_lead_bright",
           reverb=0.2, reverb_type="plate")
p.add("A4", EIGHTH).add("C5", EIGHTH).add("D5", QUARTER)
p.rest(EIGHTH).add("E5", EIGHTH).add("D5", EIGHTH).add("C5", EIGHTH)
p.add("A4", QUARTER).rest(QUARTER).add("G4", EIGHTH).add("A4", EIGHTH)
p.add("C5", HALF)
play_score(s)


# ── Ring Mod Bell ────────────────────────────────────────────────────────────
# Shimmery, metallic — sparse hits with long reverb tail.

print("\n=== RING MOD BELL ===")
s = Score("4/4", bpm=66)
p = s.part("bell", instrument="ring_mod_bell",
           reverb=0.6, reverb_type="cave", reverb_decay=3.0)
p.add("C5", HALF).rest(QUARTER).add("G4", QUARTER)
p.rest(HALF).add("E5", HALF)
p.add("D5", QUARTER).rest(QUARTER).add("C5", HALF)
p.rest(WHOLE)
p.add("G4", QUARTER).add("A4", QUARTER).add("C5", HALF)
play_score(s)


# ── Ring Mod Metallic ────────────────────────────────────────────────────────
# Alien, inharmonic — atonal stabs.

print("\n=== RING MOD METALLIC ===")
s = Score("4/4", bpm=100)
p = s.part("metal", instrument="ring_mod_metallic",
           reverb=0.4, reverb_type="parking_garage", reverb_decay=2.0)
p.add("F4", EIGHTH).rest(EIGHTH).add("Ab4", EIGHTH).add("F4", EIGHTH)
p.rest(QUARTER).add("Db5", QUARTER).rest(QUARTER)
p.add("C5", EIGHTH).add("Ab4", EIGHTH).rest(QUARTER).add("F4", HALF)
p.rest(HALF).add("Db5", QUARTER).add("C5", QUARTER)
play_score(s)


# ── Wavefold Warm ────────────────────────────────────────────────────────────
# Gentle folds — round and musical, like a filtered saw with overtones.

print("\n=== WAVEFOLD WARM ===")
s = Score("4/4", bpm=108)
p = s.part("fold", instrument="wavefold_warm",
           reverb=0.3, reverb_type="plate")
p.add("A3", QUARTER).add("C4", QUARTER).add("E4", QUARTER).add("A4", QUARTER)
p.add("G4", DOTTED_Q).add("E4", EIGHTH).add("C4", HALF)
p.add("D4", QUARTER).add("F4", QUARTER).add("A4", HALF)
p.add("G4", WHOLE)
play_score(s)


# ── Wavefold Gnarly ──────────────────────────────────────────────────────────
# Cranked folds — buzzy, aggressive, with syncopation.

print("\n=== WAVEFOLD GNARLY ===")
s = Score("4/4", bpm=130)
p = s.part("gnarly", instrument="wavefold_gnarly",
           reverb=0.2, reverb_type="spring")
p.add("E3", EIGHTH).add("E3", EIGHTH).rest(EIGHTH).add("G3", EIGHTH)
p.add("A3", EIGHTH).rest(EIGHTH).add("B3", EIGHTH).add("A3", EIGHTH)
p.add("E3", QUARTER).add("G3", EIGHTH).add("A3", EIGHTH).add("B3", QUARTER)
p.rest(QUARTER)
p.add("E4", EIGHTH).add("D4", EIGHTH).add("B3", QUARTER).add("A3", HALF)
play_score(s)


# ── Drift Saw ────────────────────────────────────────────────────────────────
# Warm, alive analog saw — the Minimoog pad.

print("\n=== DRIFT SAW (vintage VCO) ===")
s = Score("4/4", bpm=88)
p = s.part("drift", instrument="drift_saw",
           reverb=0.35, reverb_type="taj_mahal", reverb_decay=2.0)
p.add("D4", HALF).add("F4", HALF)
p.add("A4", DOTTED_Q).add("G4", EIGHTH).add("F4", QUARTER).rest(QUARTER)
p.add("D4", QUARTER).add("E4", QUARTER).add("F4", HALF)
p.add("D4", WHOLE)
play_score(s)


# ── Drift Square ─────────────────────────────────────────────────────────────
# Hollow, wobbly — 8-bit with analog soul.

print("\n=== DRIFT SQUARE ===")
s = Score("4/4", bpm=110)
p = s.part("dsq", instrument="drift_square",
           reverb=0.25, reverb_type="plate")
p.add("C4", EIGHTH).add("E4", EIGHTH).add("G4", QUARTER).add("E4", QUARTER)
p.rest(QUARTER)
p.add("A4", EIGHTH).add("G4", EIGHTH).add("E4", QUARTER).add("C4", HALF)
p.add("D4", QUARTER).add("F4", EIGHTH).add("G4", EIGHTH).add("A4", HALF)
p.add("G4", WHOLE)
play_score(s)


# ── Analog Pad ───────────────────────────────────────────────────────────────
# Slow, drifting chords — Juno-style lushness.

print("\n=== ANALOG PAD ===")
s = Score("4/4", bpm=70)
p = s.part("pad", instrument="analog_pad",
           reverb=0.5, reverb_type="taj_mahal", reverb_decay=3.0)
p.add("A3", WHOLE)
p.add("C4", HALF).add("E4", HALF)
p.add("F4", WHOLE)
p.add("E4", HALF).add("D4", HALF)
p.add("C4", WHOLE)
play_score(s)


# ── Analog Bass ──────────────────────────────────────────────────────────────
# Tight, punchy — Moog bass with filter sweep.

print("\n=== ANALOG BASS ===")
s = Score("4/4", bpm=120)
p = s.part("bass", instrument="analog_bass",
           reverb=0.1, reverb_type="plate")
p.add("E2", EIGHTH).add("E2", EIGHTH).rest(EIGHTH).add("G2", EIGHTH)
p.add("A2", QUARTER).rest(QUARTER)
p.add("E2", EIGHTH).rest(EIGHTH).add("B2", EIGHTH).add("A2", EIGHTH)
p.add("G2", QUARTER).add("E2", QUARTER).rest(HALF)
p.add("E2", EIGHTH).add("E2", EIGHTH).add("G2", EIGHTH).add("A2", EIGHTH)
p.add("B2", QUARTER).add("A2", QUARTER).add("E2", HALF)
play_score(s)


print("\nDone!")
