from ..tree import Root


def make_tree(recipe):
    root = Root()
    root.inflate(recipe)
    return root.children[0]
