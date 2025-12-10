from collections import defaultdict, deque

from representation import dimacs
from sat_solvers.utils import PartialTruthAssignment, TrackedClause, TrackedCNF, Literal


class CDCL:
    """
    A class that performs the Conflict-Driven Clause Learning (CDCL) SAT algorithm.

    The algorithm tries to find a truth assignment that validates a CNF, in order to determine
    whether the CNF is or is not satisfiable.
    """
    cnf: TrackedCNF
    v: PartialTruthAssignment
    assigned_count: int
    current_level: int
    assignments_stack: list[tuple[Literal, int, int]]  # [literal, level at which it was assigned, reason clause index]
    watchlist: dict[int, set[int]]  # [literal, list of indexes of clauses that watch it]
    propagation_queue: deque[tuple[Literal, int]]  # List of [literal, reason clause index] to propagate on
    levels: dict[int, int | None]  # [propositional letter, level at which it was assigned a truth value]

    def __init__(self, cnf: dimacs.DimacsCNF):
        self.v = PartialTruthAssignment(cnf.n_vars)
        self.assigned_count = 0
        self.current_level = 0
        self.propagation_queue = deque()
        self.assignments_stack = list()
        self.levels = dict()

        ok = self.handle_one_literal_clauses(cnf)
        assert ok, "A conflict was found just by looking at one-literal clauses"            
        self.cnf = TrackedCNF(
            clauses=[
                TrackedClause(literals=clause.literals, true_literals=[l for l, _ in list(self.propagation_queue)])
                for clause in cnf
                if len(clause) >= 2
            ],
            n_vars=cnf.n_vars,
        )
        self.init_watchlist()

    def solve(self) -> bool:
        """
        Performs the DPLL procedure on self.cnf.

        :return: True if a satisfying assignment was found. False otherwise.
        """
        while True:
            conflict_clause_idx = self.propagate()
            match conflict_clause_idx:
                case -2:  # Conflict caused by a clause with only 1 literal (so the CNF is UNSAT)
                    return False
                case -1:  # No conflict
                    if self.assigned_count == self.cnf.n_vars:
                        return True
                    decision_literal = self.choose_decision_literal()
                    self.current_level += 1
                    self.propagation_queue.append((decision_literal, -1))
                case _:  # Conflict caused by a clause with at least 2 literals
                    if self.current_level == 0: return False
                    learnt_clause, literal_to_propagate = self.learn(conflict_clause_idx, self.current_level)
                    if len(learnt_clause) == 1:  # Single-literal clauses are overall forced assignments. We do not need to learn them
                        self.backjump(0)
                        self.propagation_queue.append((list(learnt_clause)[0], -2))
                    else:
                        level = self.get_second_highest_level(learnt_clause)
                        added_idx = self.add_learnt_clause(learnt_clause)
                        self.backjump(level)
                        self.propagation_queue.append((literal_to_propagate, added_idx))

    def propagate(self) -> int:
        """
        Propagates the effects of assigning the literals in the self.propagation_queue.
        If in the process new assignments are forced to be made, they are made and propagated.

        :return: The index of the conflict clause, if the propagation reaches a conflict. -1 otherwise.
        """
        while self.propagation_queue:
            literal, reason_clause_idx = self.propagation_queue.popleft()
            current_tv : bool | None = self.v[literal]
            if current_tv == False: return reason_clause_idx  # Conflict
            if current_tv: continue
            self.assign(literal, True, reason_clause_idx)
            for clause_idx in list(self.watchlist[-literal]):
                clause = self.cnf[clause_idx]
                verified = clause.check(self.v)
                if verified: continue
                # In CDCL, there is a chance that watched literals are not correct due to backjumping
                old_watched = clause.watched
                clause.update_watched(self.v)
                new_watched = clause.watched
                for old_watch, new_watch in zip(old_watched, new_watched):
                    if old_watch == new_watch: continue
                    self.watchlist[old_watch].remove(clause_idx)
                    self.watchlist[new_watch].add(clause_idx)
                verified = clause.check(self.v)
                if verified: continue
                if verified == False: return clause_idx # Conflict
                # verified is None ---> [None, None] or [False, None]
                tv1, tv2 = self.v[new_watched[0]], self.v[new_watched[1]]
                if tv1 is None and tv2 is None: continue
                if tv1 is None:
                    none_literal = new_watched[0]
                    self.propagation_queue.append((none_literal, clause_idx))
                elif tv2 is None:
                    none_literal = new_watched[1]
                    self.propagation_queue.append((none_literal, clause_idx))
        return -1

    def learn(self, conflict_clause_idx: int, conflict_level: int) -> tuple[set[Literal], Literal]:
        """
        Starting from a conflict, it finds the clause learnt by cutting the implication graph
        on a First-UIP (Unique Implication Point). This clause should be the one that CDCL learns from the conflict.

        In order to determine the First-UIP, it uses the Resolution Rule:
        (x | C) & (!x | D) ----> (C | D)
        from the clause that caused the conflict and traversing the implication graph (the assignment stack) backwards
        until a clause with only one literal assigned at the level of the conflict is found.

        :param conflict_clause_idx: the index of the clause that caused the conflict.
        :param conflict_level: the level at which the conflict happened.
        :return: the learnt clause (as a set of literals) and the literal on which propagation should happen.
        """

        def count_literals_at_conflict_level(c: set[Literal]) -> tuple[int, Literal]:
            """Counts the number of literals at conflict level and also returns one of them"""
            l = None
            count = 0
            for literal in c:
                level = self.levels[abs(literal)]
                if level == conflict_level:
                    count += 1
                    l = literal
            assert l is not None, "There should be at least one literal at conflict level in the clause"
            return count, l

        clause = set(self.cnf[conflict_clause_idx])
        idx_on_stack = len(self.assignments_stack) - 1
        while idx_on_stack >= 0:
            count, literal = count_literals_at_conflict_level(clause)
            if count == 1:
                return clause, literal

            assigned_literal, assignment_level, reason_clause_idx = self.assignments_stack[idx_on_stack]
            if assignment_level == conflict_level and -assigned_literal in clause:
                reason_clause = set(self.cnf[reason_clause_idx])
                if assigned_literal in reason_clause:
                    clause.remove(-assigned_literal)
                    reason_clause.remove(assigned_literal)
                    clause.update(reason_clause)
            idx_on_stack -= 1

        assert False, "We should never reach the end of the stack without finding the First-UIP"

    def get_second_highest_level(self, clause: set[Literal]) -> int:
        """
        :return: the second-highest level at which a literal in the clause was assigned.
        """
        l1, l2 = 0, 0
        for literal in clause:
            level = self.levels[abs(literal)]
            assert level is not None, "All literals in the clause built through resolution should be assigned"
            if level > l1:
                l2 = l1
                l1 = level
            elif level > l2:
                l2 = level
        return l2

    def add_learnt_clause(self, clause: set[Literal]) -> int:
        """
        Adds a new learnt clause to the CNF we are trying to satisfy

        :return: the index of the clause that was added.
        """
        tracked_clause = TrackedClause(
            literals=list(clause),
            true_literals=[l for l in clause if self.v[l]]
        )
        self.cnf.clauses.append(tracked_clause)
        idx = len(self.cnf.clauses) - 1
        w1, w2 = tracked_clause.watched
        self.watchlist[w1].add(idx)
        self.watchlist[w2].add(idx)
        return idx

    def backjump(self, target_level: int):
        """
        Jumps back from all the considerations and assignments made at any level below target_level.
        """
        while self.assignments_stack and self.assignments_stack[-1][1] > target_level:
            head = self.assignments_stack.pop()
            self.unassign(head[0])

        self.current_level = target_level
        self.propagation_queue.clear()

    def assign(self, literal: Literal, tv: bool, reason_clause_idx: int = -1):
        self.v[literal] = tv
        self.assignments_stack.append((literal, self.current_level, reason_clause_idx))
        self.levels[abs(literal)] = self.current_level
        self.assigned_count += 1

    def unassign(self, literal: Literal):
        self.v[literal] = None
        self.levels[abs(literal)] = None
        self.assigned_count -= 1

    def handle_one_literal_clauses(self, cnf: dimacs.DimacsCNF) -> bool:
        """
        Checks if all the one-literal clauses are compatible with each other. If they are

        :param cnf: The input CNF
        :return: False if both a clause [p] and [-p] are present. True otherwise 
        """
        single_literals : set[Literal] = set()
        for clause in cnf.clauses:
            if len(clause) != 1: continue
            literal = clause[0]
            if -literal in single_literals:
                return False
            single_literals.add(literal)
        for l in single_literals:
            self.propagation_queue.append((l, -2))
        return True

    def init_watchlist(self):
        """Initializes the watchlist by setting which clauses are watching which literals"""
        self.watchlist = defaultdict(set)
        for idx, clause in enumerate(self.cnf):
            w1, w2 = clause.watched
            self.watchlist[w1].add(idx)
            self.watchlist[w2].add(idx)

    def choose_decision_literal(self) -> Literal:
        """
        Heuristic that chooses the next literal to set True.

        Decision is based on DLIS (Dynamic Largest Individual Sum):
        the literal that appears most often in unsatisfied clauses (only consider the watchlist)

        :return: the next literal to set True (that is, the propositional letter and how to set it)
        """
        max_v = 0
        max_literal: Literal | None = None
        for i in range(self.cnf.n_vars):
            letter = i + 1
            if self.v[letter] is not None: continue
            for sign in [-1, 1]:
                literal = letter * sign
                v = len([idx for idx in self.watchlist[literal] if not self.cnf[idx].check(self.v)])
                if v > max_v or max_literal is None:
                    max_v = v
                    max_literal = literal

        assert max_literal is not None, "The heuristic has not found any unassigned letter" 
        return max_literal
