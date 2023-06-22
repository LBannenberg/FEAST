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

        if node_type in ['numeric', 'numeric_observable', 'numeric_random']:
            from feast.tree.numeric import NumericNullary
            node = NumericNullary(ingredient)
        if node_type == 'numeric_unary':
            from feast.tree.numeric import NumericUnary
            node = NumericUnary(ingredient)
        if node_type == 'numeric_expression':
            from feast.tree.numeric import NumericBinary
            node = NumericBinary(ingredient)
        if node_type == 'numeric_branch':
            from feast.tree.numeric import NumericTernary
            node = NumericTernary(ingredient)
        if node_type == 'boolean':
            from feast.tree.boolean import Boolean
            node = Boolean(ingredient)
        if node_type == 'boolean_expression':
            from feast.tree.boolean import BooleanExpression
            node = BooleanExpression(ingredient)
        if node_type == 'boolean_observable':
            from feast.tree.boolean import BooleanObservable
            node = BooleanObservable(ingredient)
        if node_type == 'boolean_random':
            from feast.tree.boolean import BooleanRandom
            node = BooleanRandom(ingredient)
        if node_type == 'boolean_branch':
            from feast.tree.boolean import BooleanIfThenElse
            node = BooleanIfThenElse(ingredient)

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

    @abstractmethod
    def _continue_deserialization(self, recipe):
        pass

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
                'serial_index': serial_index
            }
        }

        # Collect entries from children (and their children..)
        for i, c in enumerate(self.children):
            serial_index += 1
            c_index = f"{index}.{i}"
            c_result, serial_index = c.collect_index(c_index, depth + 1, serial_index)
            result[index]['min_leaf_dist'] = min(result[index]['min_leaf_dist'], c_result[c_index]['min_leaf_dist'] + 1)
            result[index]['max_leaf_dist'] = max(result[index]['max_leaf_dist'], c_result[c_index]['max_leaf_dist'] + 1)
            result[index]['recipe'] = f"{result[index]['recipe']}|{c_result[c_index]['recipe']}"
            result.update(c_result)
        if return_serial_index:
            return result, serial_index
        return result

    def alter_node_terminal(self, index_path: Union[str, list], new_terminal: str) -> None:
        """ Alter the terminal (and type, value) of the last node of the index_path.

        We walk the index_path to the end and when we're in the LAST
         part of the path, we switch the terminal.
        """
        # Used by root note
        if type(index_path) is str:
            index_path = index_path.split('.')

        # If true, you're the final target of the index_path
        if len(index_path) == 1:
            self.terminal = new_terminal
            return

        # Push on to the next node on the path
        target_child = int(index_path[1])
        self.children[target_child].alter_node_terminal(index_path[1:], new_terminal)

    def graft_new_subtree(self, index_path, subtree_recipe) -> None:
        """ Graft a new subtree to replace the indexed node.

        :param index_path: a string like '0.0.1.0' or a list like ['0', '0', '1', '0']
        indexing self.children of successive nodes
        :param subtree_recipe: a recipe to create a new subtree on that spot
        :return: None

        This method is different from alter_node_value, because it will end
         when we are in the SECOND TO LAST part of the index_path,
         because we need to be in the parent node to graft in a new child node.
        """
        # Used by root node
        if type(index_path) is str:
            index_path = index_path.split('.')
            if len(index_path) == 1:
                raise ValueError('You cannot graft the root node.')

        # If true, one of your children must be replaced with a subtree
        if len(index_path) == 2:
            self.children[int(index_path[1])], _ = self.create(subtree_recipe)
            return

        # Push on to the next node on the path
        target_child = int(index_path[1])
        self.children[target_child].graft_new_subtree(index_path[1:], subtree_recipe)
