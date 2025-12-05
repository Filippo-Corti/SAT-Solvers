from .prop_ast import ASTNode

class PropLetter(ASTNode):
    """A propositional letter."""
    def __init__(
            self,
            label: str = ""
    ):
        super().__init__(label=label)

    def __str__(self):
        return self.label
