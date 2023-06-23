import math
from abc import ABC, abstractmethod
from typing import Union


class Tree(ABC):
    indent = ' '

    def __init__(self, terminal):
        if ':' not in terminal:
            raise ValueError
        self.terminal = terminal
        self._height = None
        self.children = []

    @staticmethod
    def create(recipe):
        if type(recipe) is str:
            recipe = recipe.split('|')
        ingredient, remaining_ingredients = recipe[0], recipe[1:]
        node_type, node_value = ingredient.split(':')
        node = None

        if 'numeric_nullary' in node_type:
            from feast.tree.numeric import NumericNullary
            node = NumericNullary(ingredient)
        if node_type == 'numeric_unary':
            from feast.tree.numeric import NumericUnary
            node = NumericUnary(ingredient)
        if node_type == 'numeric_binary':
            from feast.tree.numeric import NumericBinary
            node = NumericBinary(ingredient)
        if node_type == 'numeric_ternary':
            from feast.tree.numeric import NumericTernary
            node = NumericTernary(ingredient)

        if 'boolean_nullary' in node_type:
            from feast.tree.boolean import BooleanNullary
            node = BooleanNullary(ingredient)
        if node_type == 'boolean_unary':
            from feast.tree.boolean import BooleanUnary
            node = BooleanUnary(ingredient)
        if node_type == 'boolean_unary_num':
            from feast.tree.boolean import BooleanUnaryNum
            node = BooleanUnaryNum(ingredient)
        if node_type == 'boolean_binary':
            from feast.tree.boolean import BooleanBinary
            node = BooleanBinary(ingredient)
        if node_type == 'boolean_binary_num':
            from feast.tree.boolean import BooleanBinaryNum
            node = BooleanBinaryNum(ingredient)
        if node_type == 'boolean_ternary':
            from feast.tree.boolean import BooleanTernary
            node = BooleanTernary(ingredient)

        if node is None:
            raise ValueError(f"Cannot create node from ingredient {ingredient}")

        return [node, node._continue_deserialization(remaining_ingredients)]

    def serialize(self):
        return '|'.join([self.terminal] + [child.serialize() for child in self.children])

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

    @property
    def value(self):
        return self.terminal.split(':')[1]

    @property
    def node_type(self):
        return self.terminal.split(':')[0]

    def _continue_deserialization(self, recipe):
        if 'nullary' in self.node_type:
            return recipe
        if 'unary' in self.node_type:
            child, recipe = self.create(recipe)
            self.children.append(child)
            return recipe
        if 'binary' in self.node_type:
            child, recipe = self.create(recipe)
            self.children.append(child)
            child, recipe = self.create(recipe)
            self.children.append(child)
            return recipe
        if 'ternary' in self.node_type:
            child, recipe = self.create(recipe)
            self.children.append(child)
            child, recipe = self.create(recipe)
            self.children.append(child)
            child, recipe = self.create(recipe)
            self.children.append(child)
            return recipe
        raise ValueError(f'Could not determine how to continue deserialization for terminal: {self.terminal}')

    def __repr__(self, depth=0):
        this = f"\n{self.indent * depth}{self.terminal}"
        children = "".join([child.__repr__(depth + 1) for child in self.children])
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

    def collect_index(self, index: str = '0', depth: int = 0, serial_index: int = 0):
        return_serial_index = serial_index != 0  # only the root call should be False

        # Collect local entry
        result = {
            index: {
                'min_leaf_dist': math.inf if len(self.children) else 0,
                'max_leaf_dist': 0,
                'depth': depth,
                'node_type': self.node_type,
                'value': self.value,
                'recipe': self.serialize(),
                'num_children': len(self.children),
                'terminal': self.terminal,
                'serial_index': serial_index,
                'return_type': self.node_type.split('_')[0]
            }
        }

        # Collect entries from children (and their children..)
        for i, c in enumerate(self.children):
            serial_index += 1
            c_index = f"{index}.{i}"
            c_result, serial_index = c.collect_index(c_index, depth + 1, serial_index)
            result[index]['min_leaf_dist'] = min(result[index]['min_leaf_dist'], c_result[c_index]['min_leaf_dist'] + 1)
            result[index]['max_leaf_dist'] = max(result[index]['max_leaf_dist'], c_result[c_index]['max_leaf_dist'] + 1)
            result.update(c_result)
        if return_serial_index:
            return result, serial_index
        return result
