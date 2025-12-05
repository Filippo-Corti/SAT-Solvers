import re

from .ast import ASTNode
from .token import Token, TokenType
from .parser import parse


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

    @staticmethod
    def from_string(s: str) -> "PropFormula":
        s = PropFormula.ascii_to_unicode(s)

        tokens, label_to_id = PropFormula.tokenize(s)
        id_to_label = {v: k for k, v in label_to_id.items()}

        root = parse(tokens)
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

    def __str__(self) -> str:
        return f'PropFormula: {self.root}'