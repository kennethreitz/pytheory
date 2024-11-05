from pytheory import Chord, play, Synth, TonedScale

# Create a C minor scale.
c_minor = TonedScale(tonic="C3")["minor"]

# Create a C minor chord.
chord = Chord(
    [
        c_minor[0],  # C
        c_minor[2],  # G
    ]
)

# Play the chord
print("dissonance", chord.dissonance)
print("harmony", chord.harmony)

play(chord)
