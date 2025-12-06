class Clause:
    """
    A clause in a CNF
    """
    literals: list[list[int]]

    def __init__(self, literals: list[list[int]]) -> None:
        self.literals = literals

    def __iter__(self):
        return iter(self.literals)

    def __getitem__(self, item):
        return self.literals[item]

    def __len__(self):
        return len(self.literals)

    def __str__(self):
        return str(self.literals)
