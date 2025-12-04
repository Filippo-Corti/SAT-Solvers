from nf_conversions.CNF import to_CNF
from nf_conversions.IFNF import to_IFNF
from nf_conversions.NNF import to_NNF
from representation.parsing import parse_formula, to_compact_notation

s = "(p1 & q1) | (p2 & q2) | (p3 & q3)"

print(f"Original formula: {s}")
asp = parse_formula(to_compact_notation(s))
print(f"Parsed formula: {asp}")
asp = to_IFNF(asp)
print(f"Into IFNF: {asp}")
asp = to_NNF(asp)
print(f"Into NNF: {asp}")
asp = to_CNF(asp)
print(f"Into CNF: {asp}")
asp.flatten()
print(f"Flattened formula: {asp}")