from nf_conversions import to_IFNF, to_NNF, to_equisat_CNF
from representation import ast, dimacs
from sat_solvers import DPLL, CDCL

#s = "(x1 ∨ x2 ∨ ¬x3) ∧ (¬x2 ∨ x3)"
#s = "(!p | q | r) & (p | !q | !r) & (q | r) & (q | !r) & (!p | !q | !r)"
#s = "!(A & B) | (C -> D) -> E"
#s = "((C | D) & (C -> E)) | !(C | D) | !(C -> E)"
#s = "p & (!p | !q | r) & !r"
#s = "!1"

# f = ast.PropFormula.from_string(s)
# print(f"Input:\t{f}")
# f2 = to_IFNF(f)
# print(f"IFNF:\t{f2}")
# f3 = to_NNF(f2)
# print(f"NNF:\t{f3}")
# f4 = to_equisat_CNF(f3)
# print(f"Equisat CNF:\t{f4}")
# cnf = dimacs.DimacsCNF.from_ast(f4)

#cnf = dimacs.DimacsCNF.from_file("examples/aim/aim-50-2_0-no-1.cnf")
cnf = dimacs.DimacsCNF.from_file("examples/aim/aim-200-1_6-no-2.cnf")
#cnf = dimacs.DimacsCNF.from_file("examples/aim/aim-100-1_6-no-2.cnf") # The condition count == 1 is still false when we find a decision node
#cnf = dimacs.DimacsCNF.from_file("examples/aim/aim-200-6_0-yes1-3.cnf") # KeyError on self.levels[abs(literal)]
#cnf = dimacs.DimacsCNF.from_file("examples/008.txt")

print(f"Dimacs CNF:\t{cnf}")

cdcl = CDCL(cnf)
found = cdcl.solve()
if found:
    print(f"CNF is SAT: {cdcl.v}")
    print(cdcl.cnf.check(cdcl.v))
    for clause in cdcl.cnf:
        if not clause.check(cdcl.v):
            print(f"THIS IS NOT VALIDATED: {clause}")
else:
    print("CNF is UNSAT")