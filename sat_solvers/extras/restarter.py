from .luby_sequence import LubySequence


class Restarter:
    """
    A class that handles the restarts in CDCL.

    By "restarting" the CDCL procedure, we simply mean forcing a backjump to level 0.
    This clears all assignments, but keeps:
    - The overall forced assignments (due to single clauses).
    - The learnt clauses.

    Restarting is considered useful to exit deep branches of the solution tree and try
    a quicker resolution thanks to the cumulated knowledge.

    :ivar int restart_count: number of times CDCL has been restarted.
    :ivar int conflicts_since_restart: number of conflicts happened since the last restart.
    :ivar int restart_limit: number of conflicts that should happen before the next restart.
    """

    RESTART_BASE = 80

    def __init__(self):
        self.restart_count = 0
        self.conflicts_since_restart = 0
        self.restart_limit = self.RESTART_BASE * LubySequence.get(self.restart_count + 1)

    def on_conflict(self):
        """Increases self.conflicts_since_restart by 1."""
        self.conflicts_since_restart += 1

    def should_restart(self) -> bool:
        """Returns true if a large enough number of conflicts has happened"""
        return self.conflicts_since_restart > self.restart_limit

    def on_restart(self):
        """Computes new number of conflicts until next restart"""
        self.restart_count += 1
        self.restart_limit = self.RESTART_BASE * LubySequence.get(self.restart_count + 1)
        self.conflicts_since_restart = 0
