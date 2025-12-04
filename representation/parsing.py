from representation import AST
from enum import Enum
import re


class TokenType(Enum):
    LEFT_PAR = '('
    RIGHT_PAR = ')'
    AND = '∧'
    OR = '∨'
    NOT = '¬'
    IMPLICATION = '→'
    PROP_LETTER = 'PROP_LETTER'

    def get_index(self) -> int:
        """Returns the index in the order of precedence of the operators"""
        precedence = {
            TokenType.NOT: 3,
            TokenType.AND: 2,
            TokenType.OR: 1,
            TokenType.IMPLICATION: 0,
        }
        return precedence.get(self, -1)


type Token = tuple[TokenType, str]


def to_compact_notation(formula: str) -> str:
    """
    Converts a formula with ASCII-style operators (!, &, |, ->)
    to a formula with compact Unicode operators (¬, ∧, ∨, →).

    Args:
        formula (str): The formula using ASCII-style operators.

    Returns:
        str: The formula using compact Unicode operators.
    """
    formula = formula.replace("->", "→")
    formula = formula.replace("!", "¬")
    formula = formula.replace("&", "∧")
    formula = formula.replace("|", "∨")

    return formula


def tokenize(f: str) -> list[Token]:
    tokenizer_regex = r'\s*(?:(\w+)|(¬|∧|∨|→|↔|\(|\)))'

    tokens = list()
    for m in re.finditer(tokenizer_regex, f):
        symbol, operator = m.groups()
        if symbol:
            tokens.append((TokenType.PROP_LETTER, symbol))
        elif operator:
            tokens.append((TokenType(operator), operator))
    return tokens


def parse_formula(f: str) -> AST:
    """
    Parses a propositional formula string into an AST.
    To do so, it uses an algorithm that resembles the Shunting-Yard Algorithm.

    Args:
        f (str): The propositional formula as a string.

    Returns:
        AST: The AST representing the propositional formula.
    """
    tokens = tokenize(f)

    operators: list[Token] = []  # Stack of operators
    operands: list[AST.ASTNode] = []  # Stack of operands

    def build_node(op: Token) -> AST.ASTNode:
        op_type, _ = op
        match op_type:
            case TokenType.NOT:
                return AST.Not(operands.pop())
            case TokenType.AND:
                r, l = operands.pop(), operands.pop()
                return AST.And(l, r)
            case TokenType.OR:
                r, l = operands.pop(), operands.pop()
                return AST.Or(l, r)
            case TokenType.IMPLICATION:
                r, l = operands.pop(), operands.pop()
                return AST.Implication(l, r)
            case _:
                raise ValueError(f"Invalid operator type: {op_type}")

    for (token_type, token_label) in tokens:
        match token_type:
            case TokenType.LEFT_PAR:
                operators.append((token_type, token_label))
            case TokenType.PROP_LETTER:
                operands.append(AST.PropLetter(label=token_label))
            case TokenType.RIGHT_PAR:
                while (
                        operators and  # Until stack is not empty
                        operators[-1][0] != TokenType.LEFT_PAR # Until we reach a left parenthesis
                ):
                    op = operators.pop()
                    node = build_node(op)
                    operands.append(node)
                operators.pop()  # Also pop the left parenthesis
            case _:  # Token is AND, OR, NOT, IMPLICATION, BIIMPLICATION
                while (
                        operators and # Until stack is not empty
                        operators[-1][0] != TokenType.LEFT_PAR and # Until we reach a left parenthesis
                        operators[-1][0].get_index() >= token_type.get_index() # Until the operator on top has higher precedence
                ):
                    op = operators.pop()
                    node = build_node(op)
                    operands.append(node)
                operators.append((token_type, token_label))

    # Emptying the operator stack
    while operators:
        op = operators.pop()
        node = build_node(op)
        operands.append(node)

    return operands.pop() # There should be only one operand left

