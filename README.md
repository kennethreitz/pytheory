# PyTheory: Music Theory for Humans

This (work in progress) library attempt to make exploring music theory approachable to humans.

## Usage Example

``` {.pycon}
>>> from pytheory import TonedScale

>>> c_major = TonedScale(tonic='C4').scales['major']

>>> c_major
(<Tone C4>, <Tone D4>, <Tone E4>, <Tone F4>, <Tone G4>, <Tone A5>, <Tone B5>, <Tone C5>)

>>> c_major[0].pitch()
523.251130601197

>>> c_major[0].pitch(symbolic=True)
440*2**(1/4)

>>> c_major[0].pitch(temperament='pythagorean', symbolic=True)
14080/27
```

✨🍰✨
