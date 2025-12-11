class Clause:
    """
    A clause in a CNF.

    :ivar list[int] literals: the list of literals in the clause
    """

    def __init__(self, literals: list[int]) -> None:
        self.literals = literals

    def __iter__(self):
        return iter(self.literals)

    def __getitem__(self, item: int) -> int:
        return self.literals[item]

    def __len__(self):
        return len(self.literals)

    def __str__(self):
        return str(self.literals)
