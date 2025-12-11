import time
from collections import defaultdict, deque

from representation import dimacs
from .utils import (
    PartialTruthAssignment,
    TrackedClause,
    TrackedCNF,
    Defaults,
    CDCLOptions, AssignmentStackEntry, PropagationQueueEntry
)
from .extras import ClauseForgetter, Restarter


class CDCL:
    """
    A class that performs the Conflict-Driven Clause Learning (CDCL) SAT algorithm.

    The algorithm tries to find a truth assignment that validates a CNF, in order to determine
    whether the CNF is or is not satisfiable.

    :ivar TrackedCNF cnf: The CNF the solver should work on.
    :ivar PartialTruthAssignment v: The truth assignment being built by the solver.
    :ivar int current_level: the level of depth at which the solver is currently at.
    :ivar list[AssignmentStackEntry] assignments_stack: stack keeping track of which assignments have been made.
    :ivar dict[int, int] levels: maps each propositional letter to the level it was last assigned at.
    :ivar deque[PropagationQueueEntry] propagation_queue: queue keeping track of the literals on which the solver should propagate.
    :ivar dict[int, set[int]] watchlist: for each literal, it keeps track of which clauses are watching it.
    :ivar CDCLOptions options: options for the solver.
    :ivar int timeout_time: time at which the solver should time out.

    :ivar Heuristic heuristic: the heuristic used by the solver to decide assignments.
    :ivar ClauseForgetter forgetter: the module handling learnt clause forgetting logic.
    :ivar Restarter restarter: the module handling restarting logic.
    """

    SAT = True
    UNSAT = False

    def __init__(
            self,
            cnf: dimacs.DimacsCNF,
            options: CDCLOptions,
    ):
        self.v = PartialTruthAssignment(cnf.n_vars)
        self.current_level = 0
        self.assignments_stack: list[AssignmentStackEntry] = list()
        self.levels = dict()
        self.propagation_queue: deque[PropagationQueueEntry] = deque()
        self.watchlist = defaultdict(set)

        self.options = options
        self.timeout_time = time.time() + options.timeout_seconds

        self.heuristic = options.heuristic.get_class()(n_vars=cnf.n_vars)
        self.forgetter = ClauseForgetter()
        self.restarter = Restarter()

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
        Performs the CDCL procedure on self.cnf.

        :return: True if a satisfying assignment is found. False otherwise.
        """
        while time.time() < self.timeout_time:
            conflict_clause_idx = self.propagate()

            match conflict_clause_idx:
                case Defaults.GLOBAL_UNIT_CLAUSE_REASON:
                    # Conflict caused by a clause with only 1 literal. The CNF is therefore UNSAT.
                    return CDCL.UNSAT
                case Defaults.NO_CONFLICT:
                    # Propagation ended with no conflict. We are either finished or we should take a decision.
                    if self.v.is_total():
                        return CDCL.SAT
                    self.branch()
                case _:
                    # Conflict caused by a clause with at least 2 literals.
                    # Conflicts at level 0 imply UNSAT.
                    # In all the other cases, we should learn, backjump and start over
                    if self.current_level == 0:
                        return CDCL.UNSAT

                    self.forgetter.on_conflict()
                    self.restarter.on_conflict()
                    clause, literal = self.resolve(conflict_clause_idx, self.current_level)
                    self.learn(clause, literal)
                    self.heuristic.on_learnt_clause(clause)

        raise TimeoutError("Timed out while solving.")

    def branch(self):
        """
        Decides what the new assignment should be and pushes the decision to the propagation queue.
        Also handles restarts and forgets.
        """
        if self.restarter.should_restart() and self.options.restarts:
            self.restarter.on_restart()
            if self.forgetter.should_forget() and self.options.forgets:
                self.forgetter.on_forget()
                self.forget()
            self.restart()

        decision = self.heuristic.pick_literal(self)
        self.propagation_queue.append(PropagationQueueEntry(decision, Defaults.DECISION_CLAUSE_REASON))
        self.current_level += 1

    def propagate(self) -> int:
        """
        Propagates the effects of assigning the literals in the self.propagation_queue.
        If in the process new assignments are forced to be made, they are made and propagated.

        :return: The index of the conflict clause, if the propagation reaches a conflict. -1 otherwise.
        """
        while self.propagation_queue:
            entry = self.propagation_queue.popleft()
            current_tv = self.v[entry.literal]

            if current_tv == False:
                # We are trying to re-assign a literal. This suggests there's a conflict
                return entry.reason_clause_idx
            if current_tv:
                # The literal was already assigned to this value. We do not need to propagate again.
                continue

            # We should assign the literal, then propagate looking at the watchlist
            self.assign(entry.literal, True, entry.reason_clause_idx)
            for clause_idx in list(self.watchlist[-entry.literal]):
                clause = self.cnf[clause_idx]

                # We need to check if the assignment caused conflicts or forced new assignments
                # In CDCL, there is a chance that watched literals are not correct due to backjumping
                # We should always make sure 2-watched literals are correct before calling out a conflict
                old_watched = clause.watched
                clause.update_watched(self.v)
                new_watched = clause.watched
                for old_watch, new_watch in zip(old_watched, new_watched):
                    if old_watch == new_watch: continue
                    self.watchlist[old_watch].remove(clause_idx)
                    self.watchlist[new_watch].add(clause_idx)

                tv1, tv2 = self.v[new_watched[0]], self.v[new_watched[1]]
                if (tv1 or tv2) or (tv1 is None and tv2 is None):
                    # Verified and undecided cases are uninteresting
                    continue
                if tv1 == False and tv2 == False:
                    # The clause cannot be verified. We found a conflict
                    return clause_idx
                if tv1 is None:
                    # tv1 is None and tv2 is False. We should force first literal to True
                    self.propagation_queue.append(PropagationQueueEntry(new_watched[0], clause_idx))
                elif tv2 is None:
                    # tv1 is None and tv2 is False. We should force first literal to True
                    self.propagation_queue.append(PropagationQueueEntry(new_watched[1], clause_idx))

        return Defaults.NO_CONFLICT

    def learn(self, clause: set[int], literal: int):
        """
        Learns the clause by adding it to the set of clauses componing the CNF.
        Then, it prepares to resume the search by:
        1) Backjumping to the correct level.
        2) Queueing the literal for propagation

        :param clause: the clause to learn
        :param literal: the literal at conflict level in the First-UIP
        """
        if len(clause) == 1:
            # Single-literal clauses are overall forced assignments. We do not need to learn them (just enforce them)
            self.backjump(0)
            self.propagation_queue.append(PropagationQueueEntry(literal, Defaults.GLOBAL_UNIT_CLAUSE_REASON))
            return

        level = self.get_second_highest_level(clause)
        added_idx = self.add_clause(clause)
        self.backjump(level)
        self.propagation_queue.append(PropagationQueueEntry(literal, added_idx))

    def resolve(self, conflict_clause_idx: int, conflict_level: int) -> tuple[set[int], int]:
        """
        Starting from a conflict, it finds a learnt clause by cutting the implication graph
        on a First-UIP (Unique Implication Point). This clause should be the one that CDCL learns from the conflict.

        In order to determine the First-UIP, it uses the Resolution Rule:
        (x | C) & (!x | D) ----> (C | D)
        from the clause that caused the conflict and traversing the implication graph (the assignment stack) backwards
        until a clause with only one literal assigned at the level of the conflict is found.

        :param conflict_clause_idx: the index of the clause that caused the conflict.
        :param conflict_level: the level at which the conflict happened.
        :return: the learnt clause (as a set of literals) and the literal on which propagation should happen.
        """
        self.forgetter.increase_clause_activity(conflict_clause_idx)
        clause = set(self.cnf[conflict_clause_idx])

        idx_on_stack = len(self.assignments_stack) - 1
        while idx_on_stack >= 0:
            # Resolution stops when the resolved clause has only one literal at conflict level
            last, count = None, 0
            for lit in clause:
                if self.levels.get(abs(lit)) == conflict_level:
                    count, last = count + 1, lit
            if count == 1:
                return clause, last

            # Otherwise, read from the stack and apply resolution (if possible)
            entry = self.assignments_stack[idx_on_stack]
            if entry.level == conflict_level and -entry.literal in clause:
                reason_clause = set(self.cnf[entry.reason_clause_idx])
                if entry.literal in reason_clause:
                    clause.remove(-entry.literal)
                    reason_clause.remove(entry.literal)
                    clause.update(reason_clause)
                    self.forgetter.increase_clause_activity(entry.reason_clause_idx)
            idx_on_stack -= 1

        assert False, "We should never reach the end of the stack without finding the First-UIP"

    def get_second_highest_level(self, clause: set[int]) -> int:
        """
        :return: the second-highest level at which a literal in the clause was assigned.
        """
        l1, l2 = 0, 0
        for literal in clause:
            level = self.levels[abs(literal)]
            assert level is not None, "All literals in the clause built through resolution should be assigned"
            if level > l1:
                l1, l2 = level, l1
            elif level > l2:
                l2 = level
        return l2

    def add_clause(self, clause: set[int]) -> int:
        """
        Adds a new learnt clause to the CNF we are trying to satisfy

        :return: the index of the clause that was added.
        """
        tracked_clause = TrackedClause(
            literals=list(clause),
            true_literals=[l for l in clause if self.v[l]]
        )
        idx = self.cnf.add_learnt_clause(tracked_clause)
        w1, w2 = tracked_clause.watched
        self.watchlist[w1].add(idx)
        self.watchlist[w2].add(idx)
        return idx

    def backjump(self, target_level: int):
        """
        Jumps back from all the considerations and assignments made at any level below target_level.
        It also clears the propagation queue
        """
        while self.assignments_stack and self.assignments_stack[-1].level > target_level:
            head = self.assignments_stack.pop()
            self.unassign(head.literal)

        self.current_level = target_level
        self.propagation_queue.clear()

    def assign(self, literal: int, tv: bool, reason_clause_idx: int = -1):
        self.v[literal] = tv
        self.assignments_stack.append(AssignmentStackEntry(literal, self.current_level, reason_clause_idx))
        self.levels[abs(literal)] = self.current_level
        self.heuristic.on_assign(abs(literal), literal >= 0)

    def unassign(self, literal: int):
        self.v[literal] = None
        self.levels[abs(literal)] = None

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
                return CDCL.UNSAT
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

    def restart(self):
        """
        By "restarting" the CDCL procedure, we simply mean forcing a backjump to level 0.
        This clears all assignments, but not those that are overall forced (single clauses).
        """
        self.backjump(0)

    def forget(self):
        """
        Forgets learnt clauses that are considered not as useful anymore.

        This avoids memory requirements to explode and, most importantly, avoids excessive propagation times
        due to too many clauses to propagate on.
        """
        for idx in self.forgetter.choose_clauses_to_forget(self.cnf, self.levels):
            w1, w2 = self.cnf[idx].watched
            self.watchlist[w1].remove(idx)
            self.watchlist[w2].remove(idx)
            self.cnf.forget_learnt_clause(idx)
