import os
from representation import ast, dimacs
from preprocessing import *
from sat_solvers import DPLL, CDCL, CDCLOptions, HeuristicType
from sat_solvers.BruteForcer import BruteForcer

DATASET_DIR = "examples/logcons"

results = []

for fname in sorted(os.listdir(DATASET_DIR)):
    full_path = os.path.join(DATASET_DIR, fname)
    print(f"\n=== Running file: {fname} ===")

    formula = LogConsProblem.from_file(full_path).to_formula()
    f = ast.PropFormula.from_string(formula)

    expected = BruteForcer(f).solve()

    # Preprocess
    f2 = IFNF.to_IFNF(f)
    f3 = NNF.to_NNF(f2)
    f4 = CNF.to_equisat_CNF(f3)
    cnf = dimacs.DimacsCNF.from_ast(f4)

    # Solve
    try:
        solver = CDCL(
            cnf=cnf,
            options=CDCLOptions(
                heuristic=HeuristicType.VSIDS,
                forgets=True,
                restarts=True,
                timeout_seconds=3600
            )
        )
        found = solver.solve()
    except Exception as e:
        print(e)
        found = False

    correct = (found == expected)
    results.append(correct)

    status = "SAT" if found else "UNSAT"
    expected_status = "SAT" if expected else "UNSAT"

    print(f"→ Solver says:   {status}")
    print(f"→ Expected:      {expected_status}")
    print(f"→ Correct?       {correct}")
    if status == "SAT":
        assignment = solver.cnf.check(solver.v)
        print(f"→ Assignment?    {assignment}")
        assert assignment

print("\n=== SUMMARY ===")
n = len(results)
ok = sum(results)
print(f"Correct: {ok}/{n} ({100 * ok / n:.2f}%)")
