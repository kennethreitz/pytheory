"""Convert between MIDI note numbers, frequencies, and note names."""

from pytheory import Tone

print("MIDI ↔ Note ↔ Frequency Reference")
print("=" * 50)
print()
print(f"{'MIDI':>5s}  {'Note':>5s}  {'Freq (Hz)':>10s}  {'Octave':>6s}")
print(f"{'─' * 5}  {'─' * 5}  {'─' * 10}  {'─' * 6}")

# Show all notes from C2 to C7
for midi in range(36, 97):
    tone = Tone.from_midi(midi)
    freq = tone.frequency
    print(f"{midi:>5d}  {tone.full_name:>5s}  {freq:>10.2f}  {tone.octave:>6d}")

# Useful reference points
print()
print("Key Reference Points:")
print(f"  Lowest piano note:   A0  = MIDI {Tone.from_string('A0', system='western').midi}")
print(f"  Middle C:            C4  = MIDI {Tone.from_string('C4', system='western').midi}")
print(f"  Concert A:           A4  = MIDI {Tone.from_string('A4', system='western').midi}")
print(f"  Highest piano note:  C8  = MIDI {Tone.from_string('C8', system='western').midi}")

# Round-trip demo
print()
print("Round-trip conversions:")
for start in ["C4", "A4", "F#3", "Bb5"]:
    tone = Tone.from_string(start, system="western")
    midi = tone.midi
    freq = tone.frequency
    from_midi = Tone.from_midi(midi)
    from_freq = Tone.from_frequency(freq)
    print(f"  {start:4s} → MIDI {midi} → {from_midi.full_name:4s} | "
          f"{start:4s} → {freq:.2f} Hz → {from_freq.full_name}")
