from nf_conversions import to_IFNF, to_NNF, to_equisat_CNF
from representation import ast, dimacs
from sat_solvers import dpll

#s = "(x1 ∨ x2 ∨ ¬x3) ∧ (¬x2 ∨ x3)"
#s = "(!p | q | r) & (p | !q | !r) & (q | r) & (q | !r) & (!p | !q | !r)"
#s = "!(A & B) | (C -> D) -> E"
#s = "((C | D) & (C -> E)) | !(C | D) | !(C -> E)"
#
# f = ast.PropFormula.from_string(s)
# print(f"Input:\t{f}")
# f2 = to_IFNF(f)
# print(f"IFNF:\t{f2}")
# f3 = to_NNF(f2)
# print(f"NNF:\t{f3}")
# f4 = to_equisat_CNF(f3)
# print(f"Equisat CNF:\t{f4}")
# cnf = dimacs.DimacsCNF.from_ast(f4)

#cnf = dimacs.DimacsCNF.from_file("examples/aim/aim-50-2_0-yes1-1.cnf")
cnf = dimacs.DimacsCNF.from_file("examples/aim/aim-100-1_6-yes1-1.cnf")
#cnf = dimacs.DimacsCNF.from_file("examples/001.txt")

print(f"Dimacs CNF:\t{cnf}")

dpll = dpll.DPLL(cnf)
found = dpll.solve()
if found:
    print(f"CNF is SAT: {dpll.v}")
    print(dpll.cnf.check(dpll.v))
else:
    print("CNF is UNSAT")