from collections import defaultdict, deque

from representation import dimacs
from .heuristics import DLIS
from .utils import (
    PartialTruthAssignment,
    TrackedClause,
    TrackedCNF,
    Defaults,
    AssignmentStackEntry, PropagationQueueEntry
)


class DPLL:
    """
    A class that performs the Davis-Putnam-Logemann-Loveland (DPLL) SAT algorithm.

    The algorithm tries to find a truth assignment that validates a CNF, in order to determine
    whether the CNF is or is not satisfiable.

    :ivar TrackedCNF cnf: The CNF the solver should work on.
    :ivar PartialTruthAssignment v: The truth assignment being built by the solver.
    :ivar int current_level: the level of depth at which the solver is currently at.
    :ivar list[AssignmentStackEntry] assignments_stack: stack keeping track of which assignments have been made.
    :ivar deque[PropagationQueueEntry] propagation_queue: queue keeping track of the literals on which the solver should propagate.
    :ivar dict[int, set[int]] watchlist: for each literal, it keeps track of which clauses are watching it.
    :ivar Heuristic heuristic: the heuristic used by the solver to decide assignments.
    """

    SAT = True
    UNSAT = False

    def __init__(self, cnf: dimacs.DimacsCNF):
        self.v = PartialTruthAssignment(cnf.n_vars)
        self.current_level = 0
        self.assignments_stack: list[AssignmentStackEntry] = list()
        self.levels = dict()
        self.propagation_queue: deque[PropagationQueueEntry] = deque()
        self.watchlist = defaultdict(set)

        self.heuristic = DLIS(n_vars=cnf.n_vars)

        ok = self.handle_one_literal_clauses(cnf)
        assert ok, "A conflict was found just by looking at one-literal clauses"
        self.cnf = TrackedCNF(
            clauses=[
                TrackedClause(literals=clause.literals, true_literals=[e.literal for e in list(self.propagation_queue)])
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
        state = self.propagate()
        if not state:
            # Dead-end
            return False
        if self.v.is_total():
            # Complete assignment (after propagation, which guarantees that the assignment works)
            return True

        return self.split()

    def propagate(self) -> bool:
        """
        Propagates the effects of assigning the literals in the self.propagation_queue.
        If in the process new assignments are forced to be made, they are made and propagated.

        :return: False if the propagation reaches a dead-end. True otherwise.
        """
        while self.propagation_queue:
            entry = self.propagation_queue.popleft()
            current_tv = self.v[entry.literal]

            if current_tv == False:
                # We are trying to re-assign a literal. This suggests there's a conflict
                return False
            if current_tv:
                # The literal was already assigned to this value. We do not need to propagate again.
                continue

            # We should assign the literal, then propagate looking at the watchlist
            self.assign(entry.literal, True, entry.reason_clause_idx)
            for clause_idx in list(self.watchlist[-entry.literal]):
                clause = self.cnf[clause_idx]

                # We need to check if the assignment caused conflicts or forced new assignments
                # We can rely on the 2-watched literal mechanism, avoiding a full check of the clause
                verified = clause.check(self.v)
                if verified:
                    continue
                if verified == False:
                    return False
                swaps = clause.update_watched(self.v)
                if not swaps:  # 2-Watched are [False, None]
                    none_literal = clause.watched[0] if self.v[clause.watched[0]] is None else clause.watched[1]
                    self.propagation_queue.append(PropagationQueueEntry(none_literal, clause_idx))
                else:
                    # In DPLL, we can always assume that we will not have to change more than one watched at a time
                    old_watch, new_watch = swaps[0]
                    self.watchlist[old_watch].remove(clause_idx)
                    self.watchlist[new_watch].add(clause_idx)
        return Defaults.NO_CONFLICT

    def split(self) -> bool:
        """
        Picks an unassigned propositional letter in the current assignment and tries to solve both branches.

        :return: True if a satisfying assignment was found.
        """
        decision = self.heuristic.pick_literal(self)

        self.current_level += 1
        self.propagation_queue.append(PropagationQueueEntry(decision, Defaults.DECISION_CLAUSE_REASON))
        if self.solve():
            return True
        self.backtrack()

        self.current_level += 1
        self.propagation_queue.append(PropagationQueueEntry(-decision, Defaults.DECISION_CLAUSE_REASON))
        if self.solve():
            return True
        self.backtrack()

        return False

    def backtrack(self):
        """
        Jumps back from all the considerations and assignments made at any level below target_level.
        It also clears the propagation queue
        """
        self.current_level -= 1
        while self.assignments_stack and self.assignments_stack[-1].level > self.current_level:
            head = self.assignments_stack.pop()
            self.unassign(head.literal)

        self.propagation_queue.clear()

    def assign(self, literal: int, tv: bool, reason_clause_idx: int = -1):
        self.v[literal] = tv
        self.assignments_stack.append(AssignmentStackEntry(literal, self.current_level, reason_clause_idx))
        self.heuristic.on_assign(abs(literal), literal >= 0)

    def unassign(self, literal: int):
        self.v[literal] = None

    def handle_one_literal_clauses(self, cnf: dimacs.DimacsCNF) -> bool:
        """
        Checks if all the one-literal clauses are compatible with each other. If they are

        :param cnf: The input CNF
        :return: False if both a clause [p] and [-p] are present. True otherwise
        """
        # Check for potential opposite one-literals ([p] and [-p])
        single_literals = set()
        for c in cnf.clauses:
            if len(c) != 1:
                continue
            literal = c[0]
            if -literal in single_literals:
                return DPLL.UNSAT
            single_literals.add(literal)

        # Enqueue propagation of all single literals - they are forced assignments
        for l in single_literals:
            self.propagation_queue.append(PropagationQueueEntry(l, Defaults.GLOBAL_UNIT_CLAUSE_REASON))
        return True

    def init_watchlist(self):
        """Initializes the watchlist by setting which clauses are watching which literals"""
        for idx, c in enumerate(self.cnf):
            w1, w2 = c.watched
            self.watchlist[w1].add(idx)
            self.watchlist[w2].add(idx)
