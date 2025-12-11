from sat_solvers.heuristics.heuristic import Heuristic


class RandomChoice(Heuristic):
    """
    A class that handles a simple Heuristic that picks the branching literal randomly
    among those yet to be assigned.
    """

    def __init__(self, n_vars: int):
        super().__init__(n_vars)

    def pick_literal(self, solver: "CDCL") -> int:
        """Chooses a propositional letter and the truth value to assign to"""
        for i in range(self.n_vars):
            letter = i + 1
            if solver.v[letter] is None:
                return letter

        assert False, "The heuristic has not found any unassigned letter"