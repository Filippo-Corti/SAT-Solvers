from dataclasses import dataclass


class Defaults:
    NO_CONFLICT = -1  # The conflict clause index, in case there is no conflict clause
    GLOBAL_UNIT_CLAUSE_REASON = -2  # The reason clause for single-literal clauses
    DECISION_CLAUSE_REASON = -1  # The reason clause for a literal decided by a heuristic


@dataclass(frozen=True)
class AssignmentStackEntry:
    """
    Entry in the Assignment Stack.

    :ivar int literal: assigned literal (assumes truth value = True).
    :ivar int level: level of assignment.
    :ivar int reason_clause_idx: index of the clause that caused the forced assignment.
    """
    literal: int
    level: int
    reason_clause_idx: int


@dataclass(frozen=True)
class PropagationQueueEntry:
    """
    Entry in the Propagation Queue.

    :ivar int literal: literal to assign (assumes truth value = True).
    :ivar int reason_clause_idx: index of the clause that caused the forced assignment.
    """
    literal: int
    reason_clause_idx: int
