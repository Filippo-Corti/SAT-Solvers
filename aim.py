import os
from representation import dimacs
from sat_solvers.dpll import DPLL

AIM_DIR = "examples/aim"

def expected_answer_from_filename(filename: str) -> bool:
    """
    Returns True if filename indicates SAT, False if UNSAT.
    Assumes filenames contain either 'yes' or 'no'.
    """
    lower = filename.lower()
    if "yes" in lower:
        return True
    if "no" in lower:
        return False
    raise ValueError(f"Cannot determine expected result from filename: {filename}")

def run_all_aim():
    results = []

    for fname in sorted(os.listdir(AIM_DIR)):
        if not fname.endswith(".cnf") and not fname.endswith(".txt"):
            continue  # skip irrelevant files

        full_path = os.path.join(AIM_DIR, fname)
        print(f"\n=== Running file: {fname} ===")

        # expected SAT/UNSAT
        expected = expected_answer_from_filename(fname)

        # load CNF
        cnf = dimacs.DimacsCNF.from_file(full_path)

        # run solver
        solver = DPLL(cnf)
        found = solver.solve()

        # report
        correct = (found == expected)
        results.append(correct)

        status = "SAT" if found else "UNSAT"
        expected_status = "SAT" if expected else "UNSAT"

        print(f"→ Solver says:   {status}")
        print(f"→ Expected:      {expected_status}")
        print(f"→ Correct?       {correct}")

    # summary
    print("\n=== SUMMARY ===")
    n = len(results)
    ok = sum(results)
    print(f"Correct: {ok}/{n} ({100*ok/n:.2f}%)")

if __name__ == "__main__":
    run_all_aim()
