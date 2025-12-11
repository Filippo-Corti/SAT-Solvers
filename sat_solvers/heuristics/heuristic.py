from __future__ import annotations
from abc import ABC, abstractmethod


class Heuristic(ABC):
    """
    Abstract base class for CDCL Heuristics.

    :ivar int n_vars: the number of propositional letters in the CNF
    """

    def __init__(self, n_vars: int):
        self.n_vars = n_vars

    @abstractmethod
    def pick_literal(self, solver: 'CDCL') -> int:
        """Chooses a propositional letter and the truth value to assign to"""
        pass

    def on_assign(self, prop_letter: int, tv: bool):
        """Called when an assignment is made"""
        pass

    def on_learnt_clause(self, learnt_clause: set[int]):
        """Called when a clause is learnt"""
        pass
