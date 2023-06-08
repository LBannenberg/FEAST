from .base import Tree


def create(recipe, debug=False):
    root, _ = Tree.create(recipe, 0, debug)
    return root
