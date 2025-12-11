from dataclasses import dataclass
from enum import Enum

from sat_solvers.heuristics import RandomChoice, DLIS, VSIDS


class HeuristicType(Enum):
    RANDOM = 1
    DLIS = 2
    VSIDS = 3

    def get_class(self):
        if self == HeuristicType.RANDOM:
            return RandomChoice
        elif self == HeuristicType.DLIS:
            return DLIS
        elif self == HeuristicType.VSIDS:
            return VSIDS
        return None


@dataclass
class CDCLOptions:
    """
    Options for the CDCL solver.

    :ivar HeuristicType heuristic: the heuristic to use to decide assignments.
    :ivar bool restarts: if true, CDCL will periodically restart.
    :ivar bool forgets: if true, CDCL will periodically forget learnt clauses deemed less useful.
    :ivar int timeout_seconds: number of seconds after which the search times out
    """
    heuristic: HeuristicType
    restarts: bool
    forgets: bool
    timeout_seconds: int
