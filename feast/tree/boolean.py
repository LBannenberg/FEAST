from feast.tree.base import Tree
from typing import Union


class IfThenElse(Tree):
    node_type = 'if'

    def _continue_deserialization(self, recipe):
        child, recipe = self.create(recipe)
        self.children.append(child)

        child, recipe = self.create(recipe)
        self.children.append(child)

        child, recipe = self.create(recipe)
        self.children.append(child)

        return recipe

    def evaluate(self, observables=None) -> Union[bool, float]:
        if self.children[0].evaluate(observables):
            return self.children[1].evaluate(observables)
        return self.children[2].evaluate(observables)

    @property
    def formula(self) -> str:
        return f"IF({self.children[0].formula} ; {self.children[1].formula} ; {self.children[2].formula})"


class Boolean(Tree):
    node_type = 'boolean'

    def _continue_deserialization(self, recipe):
        return recipe

    def evaluate(self, observables=None) -> bool:
        return self.value == 'true'

    @property
    def formula(self) -> str:
        return str(self.value == 'true')


class BooleanExpression(Tree):
    node_type = 'boolean_expression'

    def _continue_deserialization(self, recipe):
        if self.value in ['not', 'truthy']:
            child, recipe = self.create(recipe)
            self.children.append(child)
        if self.value in ['and', 'or', '>', '>=', '==', '<=', '<', '!=']:
            child, recipe = self.create(recipe)
            self.children.append(child)
            child, recipe = self.create(recipe)
            self.children.append(child)
        return recipe

    def evaluate(self, observables=None) -> bool:
        first_operand = self.children[0].evaluate(observables)

        if self.value == 'not':
            return not first_operand
        if self.value == 'truthy':
            return first_operand != 0

        second_operand = self.children[1].evaluate(observables)

        if self.value == 'and':
            return first_operand and second_operand
        if self.value == 'or':
            return first_operand or second_operand
        if self.value == '>':
            return first_operand > second_operand
        if self.value == '>=':
            return first_operand >= second_operand
        if self.value == '==':
            return first_operand == second_operand
        if self.value == '<=':
            return first_operand <= second_operand
        if self.value == '<':
            return first_operand < second_operand
        if self.value == '!=':
            return first_operand != second_operand

    @property
    def formula(self) -> str:
        if self.value in ['truthy', 'not']:
            return f"{str(self.value).upper()}({self.children[0].formula})"
        return f"({self.children[0].formula} {self.value.upper()} {self.children[1].formula})"


class BooleanObservable(Tree):
    node_type = 'boolean_observable'

    def _continue_deserialization(self, recipe):
        return recipe

    def evaluate(self, observables=None) -> bool:
        return observables['boolean'][self.value]

    @property
    def formula(self) -> str:
        return self.value

    @property
    def is_static(self) -> bool:
        return False
