from abc import ABC, abstractmethod, abstractproperty
from typing import Union


class Tree(ABC):
    node_type = 'tree'
    indent = ' '

    def __init__(self, value='root'):
        self._height = None
        self.value = value
        self.children = []

    @staticmethod
    def create(recipe):
        if type(recipe) is str:
            recipe = recipe.split('|')
        ingredient, remaining_ingredients = recipe[0], recipe[1:]
        node_type, node_value = ingredient.split(':')
        node = None

        if node_type == 'numeric':
            from feast.tree.numeric import Numeric
            node = Numeric(node_value)
        if node_type == 'numeric_expression':
            from feast.tree.numeric import NumericExpression
            node = NumericExpression(node_value)
        if node_type == 'numeric_observable':
            from feast.tree.numeric import NumericObservable
            node = NumericObservable(node_value)
        if node_type == 'if':
            from feast.tree.boolean import IfThenElse
            node = IfThenElse(node_value)
        if node_type == 'boolean':
            from feast.tree.boolean import Boolean
            node = Boolean(node_value)
        if node_type == 'boolean_expression':
            from feast.tree.boolean import BooleanExpression
            node = BooleanExpression(node_value)
        if node_type == 'boolean_observable':
            from feast.tree.boolean import BooleanObservable
            node = BooleanObservable(node_value)

        if node is None:
            raise ValueError(f"Cannot create node from ingredient {node_type}:{node_value}")

        return [node, node._continue_deserialization(remaining_ingredients)]

    def serialize(self):
        return '|'.join([self.node_type + ':' + self.value]
                        + [child.serialize() for child in self.children])

    @abstractmethod
    def evaluate(self, observables=None) -> Union[bool, float]:
        pass

    @property
    def height(self):
        if len(self.children) == 0:
            return 1
        if self._height is None:
            self._height = max([child.height for child in self.children]) + 1
        return self._height

    @abstractmethod
    def _continue_deserialization(self, recipe):
        pass

    def __repr__(self, depth=0):
        this = f"\n{self.indent * depth}{self.node_type}:{self.value}"
        children = "".join([child.__repr__(depth+1) for child in self.children])
        return this + children

    @property
    @abstractmethod
    def formula(self) -> str:
        pass

    @property
    def is_static(self) -> bool:
        for child in self.children:
            if not child.is_static:
                return False
        return True
