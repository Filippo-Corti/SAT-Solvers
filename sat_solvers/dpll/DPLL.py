from collections import defaultdict, deque

from representation import dimacs
from sat_solvers.utils import PartialTruthAssignment, TrackedClause, TrackedCNF

# [prop. letter , assigned value, level at which the decision was taken]
PropLetterAssignment = tuple[int, bool, int]


class DPLL:
    """
    A class that performs the Davis-Putnam-Logemann-Loveland (DPLL) algorithm.

    The algorithm tries to find a truth assignment that validates a CNF, in order to determine
    whether the CNF is or is not satisfiable.
    """
    cnf: TrackedCNF
    v: PartialTruthAssignment
    assigned_count: int
    assignments_stack: list[PropLetterAssignment]
    watchlist: dict[int, set[int]]  # [literal, list of indexes of clauses that watch it]
    current_level: int
    propagation_queue: deque[int]  # List of literals to propagate on

    def __init__(self, cnf: dimacs.DimacsCNF):
        self.v = PartialTruthAssignment(cnf.n_vars)
        self.assigned_count = 0
        self.current_level = 0
        self.propagation_queue = deque()
        self.assignments_stack = list()

        self.handle_one_literal_clauses(cnf)
        self.cnf = TrackedCNF(
            clauses=[
                TrackedClause(literals=clause.literals, true_literals=list(self.propagation_queue))
                for clause in cnf
                if len(clause) >= 2
            ],
            n_vars=cnf.n_vars,
        )
        self.init_watchlist()

    def solve(self) -> bool:
        """
        Performs the DPLL procedure on self.cnf.

        :return: True if a satisfying assignment was found.
        """
        state = self.propagate()
        if not state:
            return False  # dead-end
        if self.assigned_count == self.cnf.n_vars:
            return True  # Complete assignment (after propagation, which guarantees that the assignment works)

        return self.split()

    def propagate(self) -> bool:
        """
        Propagates the effects of assigning the literals in the self.propagation_queue.
        If in the process new assignments are forced to be made, they are made and propagated.

        :return: False if the propagation reaches a dead-end. True otherwise.
        """
        while self.propagation_queue:
            literal = self.propagation_queue.popleft()
            current_tv = self.v[literal]
            if current_tv == False: return False # Conflict
            if current_tv: continue
            self.assign(abs(literal), literal >= 0)
            for clause_idx in self.watchlist[-literal].copy():
                clause = self.cnf[clause_idx]
                verified = clause.check(self.v)
                if verified: continue
                if verified == False: return False
                new_literal = clause.update_watched(self.v)
                if new_literal is None:  # 2-Watched are [False, None]
                    none_literal = clause.watched[0] if self.v[clause.watched[0]] is None else clause.watched[1]
                    self.propagation_queue.append(none_literal)
                else:
                    self.watchlist[-literal].remove(clause_idx)
                    self.watchlist[new_literal].add(clause_idx)
        return True

    def split(self) -> bool:
        """
        Picks an unassigned propositional letter in the current assignment and tries to solve both branches.

        :return: True if a satisfying assignment was found.
        """
        splitting_literal = self.choose_splitting_literal()
        base_level = self.current_level

        self.current_level = base_level + 1
        self.propagation_queue.append(splitting_literal)
        if self.solve():
            return True
        self.backtrack(base_level)

        self.current_level = base_level + 1
        self.propagation_queue.append(-splitting_literal)
        if self.solve():
            return True
        self.backtrack(base_level)

        return False

    def backtrack(self, target_level: int | None = None):
        """
        Jumps back from all the considerations and assignments made while exploring the dead-ending branch.
        """
        if target_level is None:
            target_level = self.current_level - 1

        # Backtrack on the assignments stack
        while self.assignments_stack and self.assignments_stack[-1][2] > target_level:
            head = self.assignments_stack.pop()
            self.unassign(head[0])

        self.current_level = target_level
        self.propagation_queue.clear()

    def assign(self, prop_letter: int, tv: bool) -> bool:
        assert prop_letter > 0
        self.v[prop_letter] = tv
        self.assignments_stack.append((prop_letter, tv, self.current_level))
        self.assigned_count += 1
        return True

    def unassign(self, prop_letter: int):
        self.v[prop_letter] = None
        self.assigned_count -= 1

    def handle_one_literal_clauses(self, cnf: dimacs.DimacsCNF):
        """
        Checks if all the one-literal clauses are compatible with each other. If they are

        :param cnf: The input CNF
        :return: The filtered list of clauses
        """
        single_literals = set()
        for clause in cnf.clauses:
            if len(clause) != 1: continue
            literal = clause[0]
            if -literal in single_literals:
                raise ValueError("CNF cannot be satisfied!")
            single_literals.add(literal)
        for l in single_literals:
            self.propagation_queue.append(l)

    def init_watchlist(self):
        """Initializes the watchlist by setting which clauses are watching which literals"""
        self.watchlist = defaultdict(set)
        for idx, clause in enumerate(self.cnf):
            w1, w2 = clause.watched
            self.watchlist[w1].add(idx)
            self.watchlist[w2].add(idx)

    def choose_splitting_literal(self) -> int:
        """
        Heuristic that chooses the next literal to split on.

        Decision is based on DLIS (Dynamic Largest Individual Sum):
        the literal that appears most often in unsatisfied clauses (only consider the watchlist)

        :return: the next literal to split on (that is, the propositional letter and how to set it)
        """
        max_v = 0
        max_literal = None
        for i in range(self.cnf.n_vars):
            letter = i + 1
            if self.v[letter] is not None: continue
            for sign in [-1, 1]:
                literal = letter * sign
                v = len([idx for idx in self.watchlist[literal] if not self.cnf[idx].check(self.v)])
                if v > max_v or max_literal is None:
                    max_v = v
                    max_literal = literal

        if not max_literal:
            raise ValueError("No valid propositional letters found")
        return max_literal
