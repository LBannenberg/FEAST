from tree.base import Tree
from typing import Union


class Root(Tree):
    node_type = 'root'

    def inflate(self, recipe):
        recipe = recipe.split('|')
        child, _ = self._create(recipe)
        self.children.append(child)

    def deflate(self):
        return self.children[0].deflate()

    def evaluate(self, observables=None) -> Union[bool, float, None]:
        if self.debug:
            print(f"\n\n{self._indent()}EVALUATE")
        if not len(self.children):
            return None
        return self.children[0].evaluate(observables)

    @property
    def height(self):
        return self.children[0].height
