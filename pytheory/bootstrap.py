from .tones import Tone
# SYSTEMS = {"western": System(tones=TONES["western"], degrees=DEGREES["western"])}

def SYSTEMS(SYSTEMS, DEGREES, TONES, System):
    western_tones = [Tone.from_string(t) for t in TONES["western"]]
    SYSTEMS = {"western": System(tones=western_tones, degrees=DEGREES["western"])}
    return SYSTEMS
