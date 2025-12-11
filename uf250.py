import os
from representation import dimacs
from sat_solvers import DPLL, CDCL
from sat_solvers.utils import CDCLOptions
from sat_solvers.utils.options import HeuristicType

AIM_DIR = "examples/uf150"

def run_all_aim():
    results = []

    for fname in sorted(os.listdir(AIM_DIR)):
        if not fname.endswith(".cnf") and not fname.endswith(".txt"):
            continue  # skip irrelevant files

        full_path = os.path.join(AIM_DIR, fname)
        print(f"\n=== Running file: {fname} ===")

        expected = not ("uuf" in fname)
        # load CNF
        cnf = dimacs.DimacsCNF.from_file(full_path)

        # run solver
        solver = CDCL(
            cnf=cnf,
            options=CDCLOptions(
                heuristic=HeuristicType.VSIDS,
                restarts=True,
                forgets=True,
                timeout_seconds=120
            )
        )
        found = solver.solve()

        # report
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

    # summary
    print("\n=== SUMMARY ===")
    n = len(results)
    ok = sum(results)
    print(f"Correct: {ok}/{n} ({100*ok/n:.2f}%)")

if __name__ == "__main__":
    run_all_aim()
