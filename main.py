from representation.parsing import parse_formula, to_compact_notation

s = "!(A & B) | (C -> D) <-> E"

asp = parse_formula(to_compact_notation(s))
print(asp)
asp.flatten()
print(asp)