from tree.base import Tree
from typing import Union


class IfThenElse(Tree):
    node_type = 'if'

    def inflate(self, recipe):
        child, recipe = self._create(recipe)
        self.children.append(child)

        child, recipe = self._create(recipe)
        self.children.append(child)

        child, recipe = self._create(recipe)
        self.children.append(child)

        return recipe

    def evaluate(self, observables=None) -> Union[bool, float]:
        if self.debug:
            print(f"{self._indent()}if:")
        if self.children[0].evaluate(observables):
            if self.debug:
                print(f"{self._indent()}then:")
            return self.children[1].evaluate(observables)
        if self.debug:
            print(f"{self._indent()}else:")
        return self.children[2].evaluate(observables)


class Boolean(Tree):
    node_type = 'boolean'

    def inflate(self, recipe):
        return recipe

    def evaluate(self, observables=None) -> bool:
        if self.debug:
            print(f"{self._indent()}[constant] : {self.value}")
        return self.value == 'true'


class BooleanExpression(Tree):
    node_type = 'boolean_expression'

    def inflate(self, recipe):
        if self.value in ['not', 'truthy']:
            child, recipe = self._create(recipe)
            self.children.append(child)
        if self.value in ['and', 'or', '>', '>=', '==', '=<', '<', '!=']:
            child, recipe = self._create(recipe)
            self.children.append(child)
            child, recipe = self._create(recipe)
            self.children.append(child)
        return recipe

    def evaluate(self, observables=None) -> bool:
        first_operand = self.children[0].evaluate(observables)
        if self.debug and self.value in ['not']:  # unary operators
            print(f"{self._indent()}boolean_expression : {self.value} {first_operand}")

        if self.value == 'not':
            return not first_operand
        if self.value == 'truthy':
            return first_operand != 0

        second_operand = self.children[1].evaluate(observables)
        if self.debug:
            print(f"{self._indent()}boolean_expression : {first_operand} {self.value} {second_operand}")

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


class BooleanObservable(Tree):
    node_type = 'boolean_observable'

    def inflate(self, recipe):
        return recipe

    def evaluate(self, observables=None) -> bool:
        if self.debug:
            print(f"{self._indent()}[observable : {self.value}]: {str(observables[self.value])}")
        return observables[self.value]
