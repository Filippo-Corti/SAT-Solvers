from representation import ast, PropFormula


def to_NNF(f: PropFormula) -> PropFormula:
    """
    Converts the given IFNF propositional formula into Negation Normal Form (NNF).

    This requires 3 transformations:
    - !!A = A
    - !(A | B) = !A & !B
    - !(A & B) = !A | !B

    :param f: A propositional formula in IFNF
    :return: an equivalent NNF formula
    """

    def transform(node: ast.ASTNode) -> ast.ASTNode:
        if isinstance(node, ast.Not) and not isinstance(node.child, ast.PropLetter):
            child = transform(node.children[0])
            if isinstance(child, ast.Not):  # !!A = A
                return transform(child.child)
            elif isinstance(child, ast.Or):  # !(A | B) = !A & !B
                return ast.And(transform(ast.Not(child.left)), transform(ast.Not(child.right)))
            elif isinstance(child, ast.And):  # !(A & B) = !A | !B
                return ast.Or(transform(ast.Not(child.left)), transform(ast.Not(child.right)))

        new_children = tuple(transform(c) for c in node.children)
        return type(node)(*new_children, label=node.label)  # Same node, new children

    new_root = transform(f.root)
    return PropFormula(
        root=new_root,
        id_to_label=f.id_to_label,
        next_free_letter=f.next_free_letter
    )
