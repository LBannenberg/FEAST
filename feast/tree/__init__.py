from .base import Tree


def create(recipe):
    root, _ = Tree.create(recipe)
    return root
