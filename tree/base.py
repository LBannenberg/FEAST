from abc import ABC, abstractmethod
from typing import Union


class Tree(ABC):
    node_type = 'tree'

    def __init__(self, value='root', depth=0, debug=False):
        self._height = None
        self.depth = depth
        self.debug = debug
        self.value = value
        self.children = []

    def deflate(self):
        return '|'.join([self.node_type + ':' + self.value]
                        + [child.deflate() for child in self.children])

    def _create(self, recipe):
        ingredient, remaining_ingredients = recipe[0], recipe[1:]
        node_type, node_value = ingredient.split(':')
        node = None

        if node_type == 'numeric':
            from tree.numeric import Numeric
            node = Numeric(node_value, self.depth + 1, self.debug)
        if node_type == 'numeric_expression':
            from tree.numeric import NumericExpression
            node = NumericExpression(node_value, self.depth + 1, self.debug)
        if node_type == 'numeric_observable':
            from tree.numeric import NumericObservable
            node = NumericObservable(node_value, self.depth + 1, self.debug)
        if node_type == 'if':
            from tree.boolean import IfThenElse
            node = IfThenElse(node_value, self.depth + 1, self.debug)
        if node_type == 'boolean':
            from tree.boolean import Boolean
            node = Boolean(node_value, self.depth + 1, self.debug)
        if node_type == 'boolean_expression':
            from tree.boolean import BooleanExpression
            node = BooleanExpression(node_value, self.depth + 1, self.debug)
        if node_type == 'boolean_observable':
            from tree.boolean import BooleanObservable
            node = BooleanObservable(node_value, self.depth + 1, self.debug)

        if node is None:
            raise ValueError(f"Cannot create node from ingredient {node_type}:{node_value}")

        return [node, node.inflate(remaining_ingredients)]

    def __repr__(self):
        this = f"\n{self._indent()}{self.node_type}:{self.value}"
        children = "".join([str(child) for child in self.children])
        return this + children

    def _indent(self):
        return self.depth * '  '

    @property
    def height(self):
        if len(self.children) == 0:
            return 1
        if self._height is None:
            self._height = max([child.height for child in self.children]) + 1
        return self._height

    @abstractmethod
    def inflate(self, recipe):
        pass

    @abstractmethod
    def evaluate(self, observables=None) -> Union[bool, float]:
        pass
