from .AST import UnaryOp, ASTNode, BinaryOp


class Not(UnaryOp):
    """A NOT operator node in the AST."""

    def __init__(
            self,
            child: ASTNode,
            label: str = "¬"
    ):
        super().__init__(child, label=label)


class And(BinaryOp):
    """An AND operator node in the AST."""

    def __init__(
            self,
            left: ASTNode,
            right: ASTNode,
            label: str = "∧"
    ):
        super().__init__(left, right, label=label)


class Or(BinaryOp):
    """An OR operator node in the AST."""

    def __init__(
            self,
            left: ASTNode,
            right: ASTNode,
            label: str = "∨"
    ):
        super().__init__(left, right, label=label)


class Implication(BinaryOp):
    """An IMPLICATION operator node in the AST."""

    def __init__(
            self,
            left: ASTNode,
            right: ASTNode,
            label: str = "→"
    ):
        super().__init__(left, right, label=label)
