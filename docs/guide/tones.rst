Working with Tones
==================

A :class:`~pytheory.tones.Tone` represents a single musical note, optionally
with an octave number (scientific pitch notation).

Creating Tones
--------------

.. code-block:: python

   from pytheory import Tone

   # From a string
   c4 = Tone.from_string("C4")
   cs4 = Tone.from_string("C#4")

   # Direct construction
   d = Tone(name="D", octave=3)

   # With a specific system
   a4 = Tone.from_string("A4", system="western")

Properties
----------

.. code-block:: python

   >>> c4 = Tone.from_string("C4")
   >>> c4.name
   'C'
   >>> c4.octave
   4
   >>> c4.full_name
   'C4'
   >>> str(c4)
   'C4'

Pitch and Frequency
-------------------

.. code-block:: python

   >>> a4 = Tone.from_string("A4", system="western")
   >>> a4.frequency
   440.0
   >>> a4.pitch()
   440.0

   # Different temperaments
   >>> a4.pitch(temperament="pythagorean")
   440.0

   # Symbolic (SymPy expression)
   >>> a4.pitch(symbolic=True)
   440

Arithmetic
----------

Tones support ``+`` and ``-`` operators for semitone math:

.. code-block:: python

   >>> c4 = Tone.from_string("C4", system="western")
   >>> c4 + 4        # Major third up
   <Tone E4>
   >>> c4 + 7        # Perfect fifth up
   <Tone G4>
   >>> c4 + 12       # Octave up
   <Tone C5>

Subtracting two tones gives the semitone distance:

.. code-block:: python

   >>> g4 = Tone.from_string("G4", system="western")
   >>> g4 - c4       # Semitone distance
   7

Comparison and Sorting
----------------------

Tones can be compared and sorted by pitch:

.. code-block:: python

   >>> c4 < g4
   True
   >>> sorted([g4, c4, e4])
   [<Tone C4>, <Tone E4>, <Tone G4>]

Equality checks note name and octave:

.. code-block:: python

   >>> c4 == "C"      # Compare with string
   True
   >>> c4 == Tone(name="C", octave=4)
   True
