from typing import Iterator

from representation import dimacs


class PartialTruthAssignment:
    """
    A partial truth assigment.

    Valid values are True, False and Unassigned (None).
    """
    d: dict[int, bool | None]
    n_keys: int

    def __init__(self, n_vars: int):
        self.d = {v + 1: None for v in range(n_vars)}
        self.n_keys = n_vars

    def __getitem__(self, i: int) -> bool | None:
        if i >= 0:
            return self.d[i]

        v = self.d[abs(i)]
        if v is None:
            return None
        return not v

    def __setitem__(self, i: int, v: bool | None):
        assert i >= 0, "Only positive integers are allowed as propositional letters"
        # TODO: simplify
        self.d[i] = v

    def __str__(self):
        return str(self.d)

    def get_random_unassigned(self) -> int | None:
        for k, v in self.d.items():
            if v is None:
                return k
        return None


class TrackedClause(dimacs.Clause):
    """
    A DIMACS Clause with the additional attributes required for SAT solving a CNF
    """
    watched: tuple[int, int]

    def __init__(self, literals: list[int], true_literals: list[int]) -> None:
        """Creates a tracked clause, determining the watched literals based on the assignment v"""
        super().__init__(literals)
        assert len(literals) >= 2
        watchable = list()
        for literal in self.literals:
            if -literal not in true_literals:
                watchable.append(literal)
                if len(watchable) == 2:
                    self.watched = tuple(watchable)
                    return

        if len(watchable) == 1:
            self.watched = (watchable[0], self.literals[0] if self.literals[0] != watchable[0] else self.literals[1])
        else:
            raise ValueError("CNF is not satisfiable!")

    def check(self, v: PartialTruthAssignment) -> bool | None:
        """
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

    def update_watched(self, v: PartialTruthAssignment) -> int | None:
        """
        Assumes that one literal in the current pair of watched is now False.
        It looks for a new literal to watch.

        :param v: The current partial assignment
        :return: The new literal if it finds it, None otherwise
        """
        for literal in self.literals:
            if literal in self.watched or v[literal] == False:
                continue
            if v[self.watched[0]] == False:
                self.watched = (literal, self.watched[1])
                return literal
            elif v[self.watched[1]] == False:
                self.watched = (self.watched[0], literal)
                return literal
        return None


class TrackedCNF(dimacs.DimacsCNF):
    """
    A DIMACS CNF with additional attributes required for SAT solving
    """
    clauses: list[TrackedClause]

    def __init__(self, clauses: list[TrackedClause], n_vars: int):
        super().__init__(clauses, n_vars)

    def __iter__(self) -> Iterator[TrackedClause]:
        return iter(self.clauses)

    def __getitem__(self, index: int) -> TrackedClause:
        return self.clauses[index]

    def check(self, v: PartialTruthAssignment) -> bool:
        all_true = True
        for clause in self:
            tv = clause.check(v)
            if not tv:
                all_true = False

        return all_true
