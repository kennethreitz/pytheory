from pprint import pprint
import pytheory
from pytheory import TonedScale, Tone

# print(c)
# print(c.subtract(1))
# print(c.add(1))
c = TonedScale(tonic="C4")["major"]
print(c[1].pitch())
# print(pytheory.western.scales)
