from pprint import pprint
import pytheory
from pytheory import TonedScale, Tone, western

c = Tone.from_string("C4", system=western)
# print(c)
# print(c.subtract(1))
# print(c.add(1))
c = TonedScale(system=pytheory.western, tonic="C4")
pprint(c.scales)
# print(pytheory.western.scales)
