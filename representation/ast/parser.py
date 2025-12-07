from .prop_formula import ASTNode
from .prop_letter import PropLetter
from .connectives import Not, And, Or, Implication
from representation.token import Token, TokenType


def parse(tokens: list[Token]) -> ASTNode:
    """
    Parses a propositional formula string into a binary AST.
    To do so, it uses an algorithm that resembles the Shunting-Yard Algorithm.

    :param tokens: The tokens composing the propositional formula

    :return: The AST representing the propositional formula.
    """
    operators: list[Token] = []  # Stack of operators
    operands: list[ASTNode] = []  # Stack of operands

    def build_node(op: Token) -> ASTNode:
        op_type, _ = op
        match op_type:
            case TokenType.NOT:
                return Not(operands.pop())
            case TokenType.AND:
                r, l = operands.pop(), operands.pop()
                return And(l, r)
            case TokenType.OR:
                r, l = operands.pop(), operands.pop()
                return Or(l, r)
            case TokenType.IMPLICATION:
                r, l = operands.pop(), operands.pop()
                return Implication(l, r)
            case _:
                raise ValueError(f"Invalid operator type: {op_type}")

    for (token_type, token_label) in tokens:
        match token_type:
            case TokenType.LEFT_PAR:
                operators.append((token_type, token_label))
            case TokenType.PROP_LETTER:
                operands.append(PropLetter(label=token_label))
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

