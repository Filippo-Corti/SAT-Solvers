from representation import AST


def to_IFNF(f: AST.ASTNode) -> AST.ASTNode:
    """
    Converts the given AST to Implication Free Normal Form (IFNF).

    This can simply be achieved by transforming A -> B into !A | B
    """
    f.children = [to_IFNF(child) for child in f.children]
    if isinstance(f, AST.Implication):
        a, b = f.children
        return AST.Or(AST.Not(a), b)
    return f
