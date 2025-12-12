
class LogConsProblem:
    """
    A class representing the logical consequence problem Γ ⊨ A.

    :ivar list[str] gamma: the theory
    :ivar str a: the consequence (or query)
    """

    def __init__(self, gamma: list[str], a: str):
        self.gamma = gamma
        self.a = a

    def __str__(self):
        s = "{\n"
        for g in self.gamma:
            s += f" {g}\n"
        s += f"{'}'} ⊨\t{self.a}\n"
        return s

    @staticmethod
    def from_file(filepath: str) -> 'LogConsProblem':
        """
        Parses a file representing a logical consequence problem

        :param filepath: the file path
        :return: a LogConsProblem instance
        """
        with open(filepath) as f:
            lines = [l.strip() for l in f]

        i = lines.index("")
        return LogConsProblem(lines[:i], lines[i + 1])

    def to_formula(self) -> str:
        """
        Transforms the logical consequence problem Γ ⊨ A into the formula
        Γ_1 ∧ Γ_2 ∧ ... ∧ Γ_n ∧ ¬A

        :return: the string representing the formula Γ_1 ∧ Γ_2 ∧ ... ∧ Γ_n ∧ ¬A
        """
        s = ''
        for g in self.gamma:
            s += f'({g}) ∧ '
        return s + f'¬({self.a})'