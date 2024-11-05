from time import sleep

from pytheory import TonedScale, Tone, CHARTS, play


# Add this constant at the top of the file, after the imports
EIGHTH_NOTE = 0.25
QUARTER_NOTE = 0.5

# Add scale definition after the constants
C_MAJOR = TonedScale(tonic="C4")


def play_note(note, t=0.1):
    # Convert scale degree (1-7) to note name (0-based index)
    scale_notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4"]
    note_name = scale_notes[note - 1]  # Subtract 1 because scale degrees are 1-based
    tone = Tone(note_name)
    play(tone, t=t * 1_000)
    sleep(t)


# Twinkle Twinkle Little Star in C major
# C C G G A A G (first line)
# F F E E D D C (second line)
# G G F F E E D (third line)
# G G F F E E D (fourth line)
# C C G G A A G (fifth line)
# F F E E D D C (sixth line)


def play_twinkle():
    # Define the patterns using scale degrees instead of note names
    line1 = [
        (1, EIGHTH_NOTE),  # C4
        (1, EIGHTH_NOTE),  # C4
        (5, EIGHTH_NOTE),  # G4
        (5, EIGHTH_NOTE),  # G4
        (6, EIGHTH_NOTE),  # A4
        (6, EIGHTH_NOTE),  # A4
        (5, QUARTER_NOTE),  # G4
    ]
    line2 = [
        (4, EIGHTH_NOTE),  # F4
        (4, EIGHTH_NOTE),  # F4
        (3, EIGHTH_NOTE),  # E4
        (3, EIGHTH_NOTE),  # E4
        (2, EIGHTH_NOTE),  # D4
        (2, EIGHTH_NOTE),  # D4
        (1, QUARTER_NOTE),  # C4
    ]
    line3 = [
        (5, EIGHTH_NOTE),  # G4
        (5, EIGHTH_NOTE),  # G4
        (4, EIGHTH_NOTE),  # F4
        (4, EIGHTH_NOTE),  # F4
        (3, EIGHTH_NOTE),  # E4
        (3, EIGHTH_NOTE),  # E4
        (2, QUARTER_NOTE),  # D4
    ]

    # Construct the full melody using the patterns
    melody = (
        line1  # Twinkle twinkle little star
        + line2  # How I wonder what you are
        + line3  # Up above the world so high
        + line3  # Like a diamond in the sky
        + line1  # Twinkle twinkle little star
        + line2  # How I wonder what you are
    )

    print("Playing Twinkle Twinkle Little Star...")
    for note, duration in melody:
        play_note(note, duration)


if __name__ == "__main__":
    play_twinkle()
