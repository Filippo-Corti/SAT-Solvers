class LubySequence:
    """
    The Luby Sequence is a theoretically optimal universal sequence of run-time limits used for restarting
    randomized "Las Vegas" algorithms.

    It is also commonly used by CDCL to determine how often the algorithm should "restart" (that is,
    backjump to level 0).

    The sequence goes 1, 1, 2, 1, 1, 2, 4, 1, 1, 2, 1, 1, 4, 8, ...
    """

    @staticmethod
    def get(i):
        """Returns the i-th element of the Luby sequence"""
        k = 1
        while (1 << k) < i + 1:
            k += 1
        if (i + 1) == (1 << k):
            return 1 << (k - 1)
        return LubySequence.get(i - (1 << (k - 1)) + 1)
