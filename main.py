from nf_conversions import to_IFNF, to_NNF
from representation import PropFormula

#s = "(x1 ∨ x2 ∨ ¬x3) ∧ (¬x2 ∨ x3)"
s = "!(A & B) | (C -> D) -> E"

f = PropFormula.from_string(s)
print(f"Input:\t{f}")
f2 = to_IFNF(f)
print(f"IFNF:\t{f2}")
f3 = to_NNF(f2)
print(f"NNF:\t{f3}")
