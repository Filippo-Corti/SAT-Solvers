import os
from representation import dimacs
from sat_solvers import DPLL, CDCL, CDCLOptions, HeuristicType

DATASET_DIR = "examples/uf150"


# Expected times:
# examples/aim -> less than 1 second with CDCL
# examples/uf150 -> around 3 minutes with CDCL, restarts and forgets
# examples/uf250 -> high variance between single instances and multiple runs, depending on reset and forget parameters

def expected_answer(filename: str) -> bool:
    lower = filename.lower()
    if "no" in lower or "uuf" in lower:
        return False
    if "yes" in lower or "uf" in lower:
        return True
    raise ValueError(f"Cannot determine expected result from filename: {filename}")


results = []

for fname in sorted(os.listdir(DATASET_DIR)):
    full_path = os.path.join(DATASET_DIR, fname)
    print(f"\n=== Running file: {fname} ===")

    expected = expected_answer(fname)

    cnf = dimacs.DimacsCNF.from_file(full_path)
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
