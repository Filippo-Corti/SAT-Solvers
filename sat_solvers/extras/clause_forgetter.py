from collections import defaultdict
from typing import Iterable

from .luby_sequence import LubySequence
from sat_solvers.utils.tracked_cnf import TrackedCNF


class ClauseForgetter:
    """
    A class that handles the forgetting of learnt clauses that are not considered particularly useful.

    This avoids memory requirements to explode and, most importantly, avoids excessive propagation times
    due to too many clauses to propagate on.

    :ivar float increase_amount: the amount to increase clause activity by.
    :ivar dict[int, float] activity: maps each clause index to the corresponding activity level
    :ivar int forgets_count: number of times learnt clauses have been filtered.
    :ivar int conflicts_since_forget: number of conflicts happened since the last forget.
    :ivar int forget_limit: number of conflicts that should happen before clauses should be filtered.
    """

    DECAY = 0.95
    MAX_ACTIVITY = 1e100
    FORGET_BASE = 400
    THRESHOLD_PERCENTAGE = 0.5

    def __init__(self):
        self.activity = defaultdict(float)
        self.increase_amount = 1.0
        self.forget_count = 0
        self.conflicts_since_forget = 0
        self.forget_limit = self.FORGET_BASE * LubySequence.get(self.forget_count + 1)

    def increase_clause_activity(self, clause_idx: int):
        """Increase clause activity by self.increase_amount"""
        self.activity[clause_idx] += self.increase_amount
        if self.activity[clause_idx] > self.MAX_ACTIVITY:
            self.normalize()

    def normalize(self):
        """Normalization is required when activity values become too high, to avoid overflow"""
        for idx in self.activity:
            self.activity[idx] /= self.MAX_ACTIVITY
        self.increase_amount /= self.MAX_ACTIVITY

    def on_conflict(self):
        """Increases the increase_amount in order to prioritize recent increases."""
        self.increase_amount /= self.DECAY
        self.conflicts_since_forget += 1

    def should_forget(self) -> bool:
        """Returns true if a large enough number of conflicts has happened"""
        return self.conflicts_since_forget > self.forget_limit

    def on_forget(self):
        """Computes new number of conflicts until next forget."""
        self.forget_count += 1
        self.forget_limit = self.FORGET_BASE * LubySequence.get(self.forget_count + 1)
        self.conflicts_since_forget = 0

    @staticmethod
    def lbd(clause: Iterable[int], levels: dict[int, int | None]) -> int:
        """
        LBD (Literal Block Distance) counts how many different levels of assignments
        are in the literals of the given clause
        """
        return len({levels.get(abs(lit), -1) for lit in clause})

    def choose_clauses_to_forget(self, cnf: TrackedCNF, levels: dict[int, int | None]) -> Iterable[int]:
        """
        Determines which learnt clauses should be forgotten.

        Criteria for keeping a clause are:
        1) It has at most 2 literals (Short clauses are considered useful)
        2) It has at most 2 LBD ("Dense" clauses are considered useful)
        3) It has an activity in the top-THRESHOLD_PERCENTAGE (Clauses with good activity are considered useful)

        :return: the indexes of clauses to forget
        """
        activities = [
            self.activity[idx + len(cnf.clauses)]
            for idx, _ in enumerate(cnf.learnt_clauses)
            if not cnf.learnt_deleted_dict[idx]
        ]
        avg_activity = sum(activities) / len(activities)
        activity_threshold = self.THRESHOLD_PERCENTAGE * avg_activity

        to_drop = list()
        for idx, clause in enumerate(cnf.learnt_clauses):
            if cnf.learnt_deleted_dict[idx]: continue
            total_idx = idx + len(cnf.clauses)
            act = self.activity[total_idx]
            if len(clause) <= 2: continue
            if ClauseForgetter.lbd(cnf[idx], levels) <= 2: continue
            if act > activity_threshold: continue
            yield total_idx
