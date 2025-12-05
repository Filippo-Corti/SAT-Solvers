# def to_CNF(f: AST.ASTNode) -> AST.ASTNode:
#     """
#     Converts the given AST to Conjunction Normal Form (CNF)
#     """
#     if ( # Literals
#             isinstance(f, AST.PropLetter) or
#             isinstance(f, AST.Not) and isinstance(f.children[0], AST.PropLetter)
#     ):
#         return f
#
#     if isinstance(f, AST.And):
#         return AST.And(*(to_CNF(child) for child in f.children))
#
#     if isinstance(f, AST.Or):
#         new_children = [to_CNF(child) for child in f.children]
#
#         # Check if of the shape (... | (A & B) | ...)
#         if all(not isinstance(child, AST.And) for child in new_children):
#             # This is already ok
#             return AST.Or(*new_children)
#
#         # Find the AND
#         first_and_child = next(child for child in new_children if isinstance(child, AST.And))
#         others = [child for child in new_children if child is not first_and_child]
#
#         # Apply Generalized Distributivity
#         # (A & B) | (C & D) | E becomes:
#         # (A | (C & D)) & (B | (C & D))
#         distributed_children = list()
#         for conjunct in first_and_child.children:
#             new_or = AST.Or(*(others + [conjunct]))
#             distributed_children.append(to_CNF(new_or)) # Recursively apply to children!
#         return AST.And(*distributed_children)
#
#     return f