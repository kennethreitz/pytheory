# PyTheory: Music Theory for Humans

This (work in progress) library attempt to make exploring music theory approachable to humans.

![logo](https://github.com/kennethreitz/pytheory/raw/master/ext/pytheory-small.png)

## Usage Example

``` {.pycon}
>>> from pytheory import TonedScale

>>> c_minor = TonedScale(tonic='C4')['minor']

>>> c_minor
<Scale I=C4 II=D4 III=Eb4 IV=F4 V=G4 VI=Ab4 VII=Bb5 VIII=C5>

>>> c_minor[0].pitch()
523.251130601197

>>> c_minor["I"].pitch(symbolic=True)
440*2**(1/4)

>>> c_minor["tonic"].pitch(temperament='pythagorean', symbolic=True)
14080/27
```

✨🍰✨
