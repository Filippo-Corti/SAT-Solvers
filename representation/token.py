from enum import Enum


class TokenType(Enum):
    """
    A type of token in the tokenization of a propositional formula.
    """
    LEFT_PAR = '('
    RIGHT_PAR = ')'
    AND = '∧'
    OR = '∨'
    NOT = '¬'
    IMPLICATION = '→'
    PROP_LETTER = 'PROP_LETTER'

    def get_index(self) -> int:
        """Returns the index in the order of precedence of the connectives"""
        precedence = {
            TokenType.NOT: 3,
            TokenType.AND: 2,
            TokenType.OR: 1,
            TokenType.IMPLICATION: 0,
        }
        return precedence.get(self, -1)


type Token = tuple[TokenType, str]
