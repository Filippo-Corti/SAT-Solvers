from typing import Iterator

from representation import dimacs


type Literal = int

class PartialTruthAssignment:
    """
    A partial truth assigment.

    Valid values are True, False and Unassigned (None).
    """
    d: dict[int, int | None]
    n_keys: int

    def __init__(self, n_vars: int):
        self.d = {v + 1: None for v in range(n_vars)}
        self.n_keys = n_vars

    def __getitem__(self, i: Literal) -> bool | None:
        if i >= 0:
            return self.d[i]

        v = self.d[abs(i)]
        if v is None:
            return None
        return not v

    def __setitem__(self, i: Literal, v: bool | None):
        if i >= 0:
            self.d[i] = v
        else:
            self.d[abs(i)] = None if v is None else not v

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
    watched: tuple[Literal, Literal]

    def __init__(self, literals: list[Literal], true_literals: list[Literal]) -> None:
        """
        Creates a tracked clause, determining the watched literals based on the assignment v.
        """
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

    def update_watched(self, v: PartialTruthAssignment):
        """
        It looks for new literals to watch.

        :param v: The current partial assignment
        """
        for literal in self.literals:
            if literal in self.watched or v[literal] == False:
                continue
            w1, w2 = self.watched
            if v[w1] == False:
                self.watched = (literal, w2)
            elif v[w2] == False:
                self.watched = (w1, literal)


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
                clause.update_watched(v)
                tv = clause.check(v)
                if not tv:
                    all_true = False

        return all_true
