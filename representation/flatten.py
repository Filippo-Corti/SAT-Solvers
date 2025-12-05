# from .ast import *
#
#
# def flatten(node: ASTNode) -> ASTNode:
#     """Allows for n-ary 'AND' and 'OR' operators. Works in place"""
#
#     new_children = []
#     for child in node.children:
#         new_child = flatten(child)
#         if isinstance(node, And) or isinstance(node, Or):
#             if isinstance(child, type(node)):
#                 new_children.extend(child.children)
#             else:
#                 new_children.append(child)
#
#     node.children = new_children
#
#     return node