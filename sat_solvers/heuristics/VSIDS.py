from __future__ import annotations
from collections import defaultdict
from heapq import heappush, heappop

from .heuristic import Heuristic


class VSIDS(Heuristic):
    """
    A class that handles a VSIDS Heuristic to pick the branching literal.

    Decision is based on VSIDS (Variable State Independent Decaying Sum):
    * the propositional letter is chosen according to their activity level, which measures how much the letter
    has appeared in recent conflicts
    * the truth value (True/False) is chosen according to the phase. If it is the first assignment, we choose False.

    :ivar dict[int, bool] phase: a dictionary that maps each propositional letter to the last value assigned to it.
    :ivar dict[int, float] activity: a dictionary that maps each propositional letter to their activity value.
    :ivar list[tuple[int, int]] heap: a min-heap structure that allows for quick extraction of high activity letters.
    :ivar float increase_amount: the increase in activity that a letter receives.
    """

    DECAY = 0.95
    MAX_ACTIVITY = 1e100

    def __init__(self, n_vars: int):
        super().__init__(n_vars)
        self.phase = dict()
        self.activity = defaultdict(float)
        self.heap = []
        self.increase_amount = 1.0

        for prop_letter in range(1, n_vars + 1):
            heappush(self.heap, (0.0, prop_letter))

    def pick_literal(self, solver: 'CDCL') -> int:
        """Chooses a propositional letter and the truth value to assign to"""
        while self.heap:
            neg_act, prop_letter = heappop(self.heap)
            if -neg_act == self.activity[prop_letter] and solver.v[prop_letter] is None:
                sign = 1 if self.phase.get(prop_letter, False) else -1
                return prop_letter * sign

        for prop_letter in range(1, self.n_vars + 1):  # Fallback
            if solver.v[prop_letter] is None:
                sign = 1 if self.phase.get(prop_letter, False) else -1
                heappush(self.heap, (-self.activity[prop_letter], prop_letter))
                return prop_letter * sign

        assert False, "The heuristic has not found any unassigned letter"


    def on_assign(self, prop_letter: int, tv: bool):
        """
        Sets the phase of the propositional letter.

        :param prop_letter: the propositional letter
        :param tv: the truth value
        """
        self.phase[prop_letter] = tv

    def on_learnt_clause(self, learnt_clause: set[int]):
        """
        Increase the activity of the propositional letters in the learnt clause

        :param learnt_clause: the set of propositional letters
        """
        for l in learnt_clause:
            self.increase_letter_activity(abs(l))
        self.increase_amount /= self.DECAY

    def increase_letter_activity(self, prop_letter: int):
        """
        Increase the activity of the propositional letter by self.increase_amount

        :param prop_letter: the propositional letter
        """
        self.activity[prop_letter] += self.increase_amount
        if self.activity[prop_letter] > self.MAX_ACTIVITY:
            self.normalize()
        heappush(self.heap, (-self.activity[prop_letter], prop_letter))

    def normalize(self):
        """Normalization is required when activity values become too high, to avoid overflow"""
        for var in self.activity:
            self.activity[var] /= self.MAX_ACTIVITY
        self.increase_amount /= self.MAX_ACTIVITY
