from __future__ import annotations
from abc import ABC, abstractmethod


class ASTNode(ABC):
    """(Abstract) Base class for all AST nodes."""
    label: str
    children: tuple["ASTNode"]

    def __init__(
            self,
            *children: ASTNode,
            label: str = ""
    ):
        if not children: children = list()
        if len(children) != self.num_children:
            raise ValueError(f"Operator {label} expects exactly {self.num_children} children, got {len(children)}")

        self.label = label
        self.children = tuple(children)

    @property
    def num_children(self) -> int:
        return 0

    @abstractmethod
    def __str__(self) -> str:
        pass


class UnaryOp(ASTNode, ABC):

    @property
    def num_children(self) -> int:
        return 1

    @property
    def child(self) -> ASTNode:
        return self.children[0]

    def __str__(self) -> str:
        return f"({self.label}{self.child})"


class BinaryOp(ASTNode, ABC):

    @property
    def num_children(self) -> int:
        return 2

    @property
    def left(self) -> ASTNode:
        return self.children[0]

    @property
    def right(self) -> ASTNode:
        return self.children[1]

    def __str__(self) -> str:
        return f"({self.left} {self.label} {self.right})"
