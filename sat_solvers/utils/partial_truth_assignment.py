class PartialTruthAssignment:
    """
    A partial truth assigment.

    Valid values are True, False and Unassigned (None).

    :ivar list[bool | None] d: dictionary representing the assignment.
    :ivar int n_keys: number of propositional letters involved in the assignment.
    :ivar int assigned_count: number of propositional letters with a non-None truth value.
    """
    d: list[bool | None]
    n_keys: int
    assigned_count: int

    def __init__(self, n_vars: int):
        self.d = [None] * n_vars
        self.n_keys = n_vars
        self.assigned_count = 0

    def __getitem__(self, i: int) -> bool | None:
        """Returns the value of the literal i"""
        if i > 0:
            return self.d[i - 1]

        v = self.d[abs(i) - 1]
        if v is None:
            return None
        return not v

    def __setitem__(self, i: int, v: bool | None):
        """Sets the value of the literal i"""
        if v is not None:
            self.assigned_count += 1
        else:
            self.assigned_count -= 1

        if i > 0:
            self.d[i - 1] = v
        else:
            self.d[abs(i) - 1] = None if v is None else not v

    def __str__(self):
        return str(self.d)

    def is_total(self) -> bool:
        return self.assigned_count == self.n_keys