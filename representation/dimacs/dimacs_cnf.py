from representation import ast
from .clause import Clause


class DimacsCNF:
    """
    A class that represents a propositional formula in CNF (Conjunctive Normal Form).

    It represents it as a list of clauses.

    :ivar list[int] clauses: the list of clauses in the CNF
    :ivar int n_vars: the number of variables in the CNF
    """

    def __init__(self, clauses: list[Clause], n_vars: int) -> None:
        self.clauses = clauses
        self.n_vars = n_vars

    @staticmethod
    def from_file(path: str) -> "DimacsCNF":
        """
        Reads the specified file and returns the corresponding DIMACS CNF.

        :param path: the path to the file
        :return: the DIMACS CNF
        """
        clauses = list()
        n_vars = -1
        for line in open(path):
            line = line.strip()
            if not line: continue
            if line[0] == 'c':
                continue
            if line[0] == 'p':
                tokens = line.split(' ')
                if n_vars == -1:
                    n_vars = int(tokens[2])
            else:
                tokens = line.split(' ')
                clause = Clause(
                    literals=[int(t) for t in tokens[:-1]]
                )
                clauses.append(clause)

        return DimacsCNF(
            clauses,
            n_vars=n_vars
        )

    @staticmethod
    def from_ast(f: ast.PropFormula) -> "DimacsCNF":
        """
        Converts a propositional formula represented as an AST into a DIMACS CNF representation.

        Assumes the AST to be in CNF.

        :param f: the AST propositional formula
        :return: the same formula, in DIMACS CNF format
        """

        def extract_clause(node):
            if isinstance(node, ast.Or):
                literals = []
                for c in node.children:
                    literals.extend(extract_clause(c))
                return literals

            if isinstance(node, ast.PropLetter):
                return [int(node.label)]

            if isinstance(node, ast.Not):
                return [-int(node.child.label)]

            raise ValueError(f"The AST does not appear to be in CNF")

        def extract_cnf(node):
            if isinstance(node, ast.And):
                cs = list()
                for c in node.children:
                    cs.extend(extract_cnf(c))
                return cs

            return [extract_clause(node)]  # Single clause

        clauses = [Clause(c) for c in extract_cnf(f.root)]
        return DimacsCNF(
            clauses=clauses,
            n_vars=f.next_free_letter - 1
        )

    def __iter__(self):
        return iter(self.clauses)

    def __getitem__(self, index: int) -> Clause:
        return self.clauses[index]

    def __str__(self):
        return ", ".join(f"{clause}" for clause in self.clauses)
