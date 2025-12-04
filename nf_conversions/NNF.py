from representation import AST


def to_NNF(f: AST.ASTNode) -> AST.ASTNode:
    """
    Converts the given AST to Negation Normal Form (NNF)
    """
    if isinstance(f, AST.PropLetter):
        return f
    if isinstance(f, AST.Not) and not isinstance(f.children[0], AST.PropLetter):
        c = to_NNF(f.children[0])
        if isinstance(c, AST.Not): # !!A = A
            return to_NNF(c.children[0])
        elif isinstance(c, AST.Or): # !(A | B) = !A & !B
            new_children = [to_NNF(AST.Not(child)) for child in c.children]
            return AST.And(*new_children)
        elif isinstance(c, AST.And): # !(A & B) = !A | !B
            new_children = [to_NNF(AST.Not(child)) for child in c.children]
            return AST.Or(*new_children)

    return type(f)(*(to_NNF(child) for child in f.children))
