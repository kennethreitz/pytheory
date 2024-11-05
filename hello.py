from pytheory import Tone, Fretboard, CHARTS

# Create standard tuning (from high E to low E)
standard_tuning = [
    Tone.from_string("E4"),  # High E
    Tone.from_string("B3"),  # B
    Tone.from_string("G3"),  # G
    Tone.from_string("D3"),  # D
    Tone.from_string("A2"),  # A
    Tone.from_string("E2"),  # Low E
]

# Create fretboard with standard tuning
fretboard = Fretboard(tones=standard_tuning)

# Define flat to sharp note mappings (updated to include all possible flats)
flat_to_sharp = {"Ab": "G#", "Bb": "A#", "Db": "C#", "Eb": "D#", "Gb": "F#"}

# Add sharp to flat mappings
sharp_to_flat = {v: k for k, v in flat_to_sharp.items()}

# Get all available chords from CHARTS
all_chords = sorted(CHARTS["western"].keys())

print("Standard Guitar Chord Charts:")
print("-" * 30)

for chord_name in all_chords:
    # Store original chord name for lookup
    lookup_name = chord_name

    # Convert flat notation to sharp only for display
    base_note = chord_name.rstrip("dim7956maj")
    if base_note in flat_to_sharp:
        # Replace the base note with its sharp equivalent for display only
        sharp_base = flat_to_sharp[base_note]
        sharp_name = chord_name.replace(base_note, sharp_base)
        print(f"    Converting {chord_name} to {sharp_name}")  # Debug line
        display_name = sharp_name
    else:
        display_name = chord_name

    chord = CHARTS["western"][lookup_name]  # Use original name for lookup

    try:
        fingering = chord.fingering(fretboard=fretboard)
        print(f"{display_name}: {fingering}")
    except Exception as e:
        print(f"{display_name}: Unable to calculate fingering - {str(e)}")
        # Add more detailed debug information
        print(f"Debug - Chord data: {chord}")
        print(
            f"Debug - Chord tones: {chord.tones if hasattr(chord, 'tones') else 'No tones available'}"
        )
        print(f"Debug - Fretboard tuning: {[str(t) for t in fretboard.tones]}")
        print(f"Debug - Available fretboard tones: {[str(t) for t in fretboard.tones]}")
