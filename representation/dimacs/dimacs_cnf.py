from representation import ast
from .clause import Clause


class DimacsCNF:
    """
    A class that represents a propositional formula in CNF (Conjunctive Normal Form).

    It represents it as a list of clauses.
    """
    clauses: list[Clause]
    n_vars: int
    v_clauses: int

    def __init__(
            self,
            clauses: list[Clause],
            n_vars: int
    ) -> None:
        self.clauses = clauses
        self.n_vars = n_vars
        self.v_clauses = len(clauses)

    @staticmethod
    def from_file(path: str) -> "DimacsCNF":
        from .parser import parse
        return parse(path)

    @staticmethod
    def from_ast(f: ast.PropFormula) -> "DimacsCNF":
        """
        Converts a propositional formula represented as an AST into a DIMACS CNF representation.

        Assumes the AST to be in CNF.

        :param f: the AST propositional formula
        :return: the same formula, in DIMACS CNF format
        """
        clauses = list()
        current_clause = list()

        def traverse(node: ast.ASTNode, in_or: bool):
            nonlocal current_clause

            if isinstance(node, ast.PropLetter):
                current_clause.append(int(node.label))
                return

            if isinstance(node, ast.Not):
                current_clause.append(-int(node.child.label))
                return

            if isinstance(node, ast.Or):
                if not in_or:
                    if current_clause:
                        clauses.append(Clause(current_clause))
                        current_clause = list()
                    in_or = True

            for child in node.children:
                traverse(child, in_or)

        traverse(f.root, False)
        if current_clause:
            clauses.append(Clause(current_clause))
        return DimacsCNF(
            clauses=clauses,
            n_vars=f.next_free_letter - 1
        )

    def __iter__(self):
        return iter(self.clauses)

    def __str__(self):
        return ", ".join(f"{clause}" for clause in self.clauses)
