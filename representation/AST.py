from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from abc import ABC, abstractmethod

""" 
An AST is an Abstract Syntax Tree. In this case, we use it to represent a formula from Propositional Logic
"""

type AST = ASTNode



@dataclass
class ASTNode(ABC):
    """(Abstract) Base class for all AST nodes."""
    label: str
    children: List["ASTNode"] = field(default_factory=list)

    @property
    def arity(self) -> int:
        return len(self.children)

    def add_child(self, child: "ASTNode"):
        self.children.append(child)

    @abstractmethod
    def __str__(self) -> str:
        pass

    def flatten(self):
        """Allows for n-ary AND and OR operators. Works in place"""
        for child in self.children: # Flatten children first (go until the leaves of the tree)
            child.flatten()
        if isinstance(self, And) or isinstance(self, Or):
            new_children = []
            for child in self.children:
                if isinstance(child, type(self)):
                    new_children.extend(child.children)
                else:
                    new_children.append(child)
            self.children = new_children

@dataclass
class PropLetter(ASTNode):
    """A propositional letter in the AST."""

    def __init__(self, label: str):
        super().__init__(label)

    def __str__(self) -> str:
        return self.label


@dataclass
class UnaryOp(ASTNode, ABC):
    """A unary operator node in the AST."""

    def __init__(self, label: str, child: ASTNode):
        super().__init__(label, [child])

    def __str__(self) -> str:
        return f"({self.label}{self.children[0]})"


@dataclass
class Not(UnaryOp):
    """A NOT operator node in the AST."""

    def __init__(self, child: ASTNode):
        super().__init__("¬", child)


@dataclass
class NaryOp(ASTNode, ABC):
    """A base class for n-ary operators (AND, OR)."""

    def __init__(self, label: str, *children: ASTNode):
        super().__init__(label, list(children))

    def __str__(self) -> str:
        joined = f" {self.label} ".join(str(c) for c in self.children)
        return f"({joined})"


@dataclass
class And(NaryOp):
    """An AND operator node in the AST."""

    def __init__(self, *children: ASTNode):
        super().__init__("∧", *children)


@dataclass
class Or(NaryOp):
    """An OR operator node in the AST."""

    def __init__(self, *children: ASTNode):
        super().__init__("∨", *children)


@dataclass
class BinaryOp(ASTNode, ABC):
    """A binary operator node for operators that are not n-ary (Implication, BiImplication)."""

    def __init__(self, label: str, left: ASTNode, right: ASTNode):
        super().__init__(label, [left, right])

    def __str__(self) -> str:
        return f"({self.children[0]} {self.label} {self.children[1]})"


@dataclass
class Implication(BinaryOp):
    """An IMPLICATION operator node in the AST."""

    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__("→", left, right)


@dataclass
class BiImplication(BinaryOp):
    """A BIIMPLICATION operator node in the AST."""

    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__("↔", left, right)
