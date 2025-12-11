import re

from .AST import ASTNode, PropLetter
from .connectives import Not, And, Or, Implication
from ..token import Token, TokenType


class PropFormula:
    """
    A PropFormula represents a formula of propositional logic with its attributes.
    """

    root: ASTNode
    id_to_label: dict[int, str]
    next_free_letter: int

    def __init__(
            self,
            root: ASTNode,
            id_to_label: dict[int, str],
            next_free_letter: int | None = None,
    ):
        self.root = root
        self.id_to_label = id_to_label

        if next_free_letter is None:
            next_free_letter = max(id_to_label.keys()) + 1
        self.next_free_letter = next_free_letter

    def __str__(self) -> str:
        return f'{self.root}'

    @staticmethod
    def from_string(s: str) -> "PropFormula":
        s = PropFormula.ascii_to_unicode(s)

        tokens, label_to_id = PropFormula.tokenize(s)
        id_to_label = {v: k for k, v in label_to_id.items()}

        root = PropFormula.parse(tokens)
        return PropFormula(root, id_to_label)

    @staticmethod
    def ascii_to_unicode(s: str) -> str:
        """
        Converts s with ASCII-style operators (!, &, |, ->)
        to a new string with Unicode operators (¬, ∧, ∨, →).

        :param s: The formula using ASCII-style operators.

        :return: The formula using Unicode operators.
        """
        for old_connective, new_connective in {
            '->': '→',
            '!': '¬',
            '&': '∧',
            '|': '∨'
        }.items():
            s = s.replace(old_connective, new_connective)

        return s

    @staticmethod
    def tokenize(s: str) -> tuple[list[Token], dict[str, int]]:
        """
        Tokenizes a string as a propositional formula.
        In the process, it transforms all propositional letters into numbers.

        :param s: The string to tokenize.
        :return: The list of tokens, the dictionary mapping each propositional letter to the new number.
        """
        tokenizer_regex = r'\s*(?:(\w+)|(¬|∧|∨|→|↔|\(|\)))'

        current_id = 1
        label_to_id = {}
        tokens = list()
        for m in re.finditer(tokenizer_regex, s):
            symbol, operator = m.groups()
            if symbol:
                symbol_id = label_to_id.get(symbol)
                if symbol_id is None:
                    label_to_id[symbol] = current_id
                    symbol_id = current_id
                    current_id += 1
                tokens.append((TokenType.PROP_LETTER, f"{symbol_id}"))
            elif operator:
                tokens.append((TokenType(operator), operator))

        return tokens, label_to_id

    @staticmethod
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
                            operators[-1][0] != TokenType.LEFT_PAR  # Until we reach a left parenthesis
                    ):
                        op = operators.pop()
                        node = build_node(op)
                        operands.append(node)
                    operators.pop()  # Also pop the left parenthesis
                case _:  # Token is AND, OR, NOT, IMPLICATION, BIIMPLICATION
                    while (
                            operators and  # Until stack is not empty
                            operators[-1][0] != TokenType.LEFT_PAR and  # Until we reach a left parenthesis
                            operators[-1][0].get_index() >= token_type.get_index()
                            # Until the operator on top has higher precedence
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

        return operands.pop()  # There should be only one operand left
