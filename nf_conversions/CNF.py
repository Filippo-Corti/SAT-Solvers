from representation import ast, PropFormula


def to_equisat_CNF(f: PropFormula) -> PropFormula:
    """
    Converts the given NNF propositional formula into an equisatisfiable Conjunctive Normal Form (CNF).

    The process employed is the following:
    1) Find any violation of the form A | (B & C)
    2) Replace (B & C) with a fresh propositional letter X
    3) Add to the tail of the formula the two clauses (!X | B) and (!X | C)

    :param f: A propositional formula in NNF
    :return: an equisatisfiable CNF formula
    """
    next_free_letter = f.next_free_letter
    id_to_label = f.id_to_label.copy()
    tail: ast.And | None = None

    def transform(node: ast.ASTNode, in_or: bool = False) -> ast.ASTNode:
        nonlocal next_free_letter
        nonlocal tail

        if isinstance(node, ast.Or):
            in_or = True
        new_children = tuple(transform(c, in_or) for c in node.children)

        if in_or and isinstance(node, ast.And):
            next_letter_label = f"{next_free_letter}"
            new_tail_clauses = ast.And(
                ast.Or(
                    left=ast.Not(ast.PropLetter(next_letter_label)),
                    right=new_children[0]
                ),
                ast.Or(
                    left=ast.Not(ast.PropLetter(next_letter_label)),
                    right=new_children[1]
                )
            )
            tail = new_tail_clauses if not tail else ast.And(new_tail_clauses, tail)
            id_to_label[next_free_letter] = next_letter_label
            next_free_letter += 1
            return ast.PropLetter(next_letter_label)

        return type(node)(*new_children, label=node.label)  # Same node, new children

    new_root = transform(f.root)
    if tail is not None:
        new_root = ast.And(new_root, tail)
    return PropFormula(
        root=new_root,
        id_to_label=id_to_label,
        next_free_letter=next_free_letter
    )
