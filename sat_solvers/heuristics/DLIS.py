from __future__ import annotations
from .heuristic import Heuristic


class DLIS(Heuristic):
    """
    A class that handles a DLIS Heuristic to pick the branching literal.

    Decision is based on DLIS (Dynamic Largest Individual Sum):
    the literal that appears most often in unsatisfied clauses (only consider the watchlist)
    """

    def __init__(self, n_vars: int):
        super().__init__(n_vars)

    def pick_literal(self, solver: 'CDCL') -> int:
        """Chooses a propositional letter and the truth value to assign to"""
        max_v = 0
        max_literal: int | None = None
        for i in range(self.n_vars):
            letter = i + 1
            if solver.v[letter] is not None: continue
            for sign in [-1, 1]:
                literal = letter * sign
                v = len([idx for idx in solver.watchlist[literal] if not solver.cnf[idx].check(solver.v)])
                if v > max_v or max_literal is None:
                    max_v = v
                    max_literal = literal

        assert max_literal is not None, "The heuristic has not found any unassigned letter"
        return max_literal
