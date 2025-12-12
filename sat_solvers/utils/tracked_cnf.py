from typing import Iterator

from .partial_truth_assignment import PartialTruthAssignment
from representation import dimacs


class TrackedClause(dimacs.Clause):
    """
    A DIMACS Clause with the additional attributes required for SAT solving a CNF.

    :ivar tuple[int, int] watched: the pair of literals that the clause is currently "watching".
    """

    def __init__(self, literals: list[int], true_literals: list[int]) -> None:
        """Creates a tracked clause, avoiding watching false literals."""
        super().__init__(literals)
        assert len(literals) >= 2
        watchable = list()
        for l in self.literals:
            if -l not in true_literals:
                watchable.append(l)
                if len(watchable) == 2:
                    self.watched = tuple(watchable)
                    return

        assert watchable, f"There are not enough watchable literals to satisfy the clause clause {self.literals}"
        self.watched = (watchable[0], self.literals[0] if self.literals[0] != watchable[0] else self.literals[1])

    def check(self, v: PartialTruthAssignment) -> bool | None:
        """
        Checks if v validates the clause, looking only at the watched literals.

        :return:
        Returns True if the clause is validated by v.
        Returns False if the clause is invalidated by v.
        Returns None if v does not specify enough propositional letters for either of the conclusions.
        """
        tv1, tv2 = v[self.watched[0]], v[self.watched[1]]
        if tv1 or tv2:
            return True
        if tv1 == False and tv2 == False:
            return False
        return None

    def deep_check(self, v: PartialTruthAssignment) -> bool | None:
        """
        Checks if v validates the clause, looking at all literals.

        :return:
        Returns True if the clause is validated by v.
        Returns False if the clause is invalidated by v.
        Returns None if v does not specify enough propositional letters for either of the conclusions.
        """
        for l in self.literals:
            tv = v[l]
            if tv:
                return True
            if tv is None:
                return None
        return False

    def update_watched(self, v: PartialTruthAssignment) -> list[tuple[int, int]]:
        """
        It looks for new literals to watch.

        :param v: The current partial assignment
        :return: The pairs of old and new watched literals
        """
        w1, w2 = self.watched
        tv1, tv2 = v[w1], v[w2]
        if tv1 or tv2:
            return list()

        literals = list()
        for l in self.literals:
            tv_new = v[l]
            if l in self.watched or tv_new == False:
                continue
            if tv1 == False:
                self.watched = (l, w2)
                literals.append((w1, l))
                w1, tv1 = l, tv_new
            elif tv2 == False:
                self.watched = (w1, l)
                literals.append((w2, l))
                w2, tv2 = l, tv_new
            else:
                return literals
        return literals


class TrackedCNF(dimacs.DimacsCNF):
    """
    A DIMACS CNF with additional attributes required for SAT solving.

    Most importantly, it allows for clauses to be learnt and forgotten.

    :ivar list[TrackedClause] watched: the list of original clauses.
    :ivar list[TrackedClause] learnt_clauses: the list of clauses learnt during solving.
    :ivar list[bool] learnt_deleted_dict: tracks which learnt clauses have been deleted. This avoids changing
    indexes in the list and thus having to update any other data structure referencing indexes (like the watchlist).
    """

    def __init__(self, clauses: list[TrackedClause], n_vars: int):
        super().__init__(clauses, n_vars)
        self.learnt_clauses = list()
        self.learnt_deleted_dict = list()

    def __iter__(self) -> Iterator[TrackedClause]:
        """Iterates over the original clauses and the non-deleted learnt clauses in the CNF"""
        for c in self.clauses:
            yield c
        for idx, c in enumerate(self.learnt_clauses):
            if not self.learnt_deleted_dict[idx]:
                yield c

    def learnt_clauses_iterator(self) -> Iterator[TrackedClause]:
        for idx, c in enumerate(self.learnt_clauses):
            if not self.learnt_deleted_dict[idx]:
                yield c

    def __getitem__(self, index: int) -> TrackedClause:
        if index < len(self.clauses):
            return self.clauses[index]
        else:
            return self.learnt_clauses[index - len(self.clauses)]

    def add_learnt_clause(self, clause: TrackedClause) -> int:
        """Adds a clause to the learnt clauses and returns its index"""
        self.learnt_clauses.append(clause)
        self.learnt_deleted_dict.append(False)
        return len(self.clauses) + len(self.learnt_clauses) - 1

    def forget_learnt_clause(self, index: int):
        """Marks a learnt clause as deleted"""
        real_idx = index - len(self.clauses)
        assert 0 <= real_idx < len(self.learnt_clauses), "Invalid learnt clause index"
        self.learnt_deleted_dict[real_idx] = True

    def check(self, v: PartialTruthAssignment) -> bool:
        """Checks if v validates the clause"""
        all_true = True
        for clause in self:
            tv = clause.deep_check(v)
            if not tv:
                all_true = False

        return all_true

