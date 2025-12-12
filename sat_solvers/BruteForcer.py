from representation import ast


class BruteForcer:
    """
    A Brute Force Solver for Propositional Formulas.

    It tries all possible combinations and checks their validity, in order to
    determine if the formula is SAT or UNSAT.

    :ivar ast.PropFormula f: the formula to verify.
    :ivar int n_vars: the number of variables in the formula.
    """

    def __init__(self, f: ast.PropFormula):
        self.f = f
        self.n_vars = f.next_free_letter - 1

    def solve(self) -> bool:
        """
        Performs the Brute-Force procedure on self.f.

        :return: True if a satisfying assignment was found. False otherwise.
        """
        valuation: list[int | None] = [None] * self.n_vars
        root = self.f.root

        for mask in range(1 << self.n_vars):  # 2^n possible assignments

            for i in range(self.n_vars):
                valuation[i] = bool((mask >> i) & 1)  # Given the number mask, we extract the i-th binary bit

            # Evaluate the formula under this assignment
            if self.evaluate(root, valuation):
                return True

        return False

    def evaluate(self, node: ast.ASTNode, valuation: list[int | None]):
        if isinstance(node, ast.PropLetter):
            tv = valuation[int(node.label) - 1]
            return bool(tv)

        if isinstance(node, ast.Not):
            return not self.evaluate(node.child, valuation)

        if isinstance(node, ast.And):
            left = self.evaluate(node.left, valuation)
            right = self.evaluate(node.right, valuation)
            return left and right

        if isinstance(node, ast.Or):
            left = self.evaluate(node.left, valuation)
            right = self.evaluate(node.right, valuation)
            return left or right

        if isinstance(node, ast.Implication):
            left_val = self.evaluate(node.left, valuation)
            right_val = self.evaluate(node.right, valuation)
            return (not left_val) or right_val

        assert False, f"Unknown AST node type: {type(node)}"
