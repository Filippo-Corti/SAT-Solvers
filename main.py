from nf_conversions import to_IFNF, to_NNF
from nf_conversions.CNF import to_equisat_CNF
from representation import PropFormula
from representation.dimacs import DimacsCNF

#s = "(x1 ∨ x2 ∨ ¬x3) ∧ (¬x2 ∨ x3)"
s = "!(A & B) | (C -> D) -> E"

f = PropFormula.from_string(s)
print(f"Input:\t{f}")
f2 = to_IFNF(f)
print(f"IFNF:\t{f2}")
f3 = to_NNF(f2)
print(f"NNF:\t{f3}")
f4 = to_equisat_CNF(f3)
print(f"Equisat CNF:\t{f4}")

cnf = DimacsCNF.from_ast(f4)
print(f"Dimacs CNF:\t{cnf}")