from representation import ast


def to_IFNF(f: ast.PropFormula) -> ast.PropFormula:
    """
    Converts the given propositional formula into Implication Free Normal Form (IFNF).

    This can simply be achieved by transforming A -> B into !A | B.

    :param f: A propositional formula
    :return: an equivalent IFNF formula
    """

    def transform(node: ast.ASTNode) -> ast.ASTNode:
        if isinstance(node, ast.Implication): # A -> B = !A | B
            left_new = transform(node.left)
            right_new = transform(node.right)
            return ast.Or(ast.Not(left_new), right_new)

        new_children = tuple(transform(c) for c in node.children)
        return type(node)(*new_children, label=node.label)  # Same node, new children

    new_root = transform(f.root)
    return ast.PropFormula(
        root=new_root,
        id_to_label=f.id_to_label,
        next_free_letter=f.next_free_letter
    )
