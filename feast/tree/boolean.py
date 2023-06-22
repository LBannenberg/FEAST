import random
from feast.tree.base import Tree


class BooleanNullary(Tree):
    def evaluate(self, observables=None) -> bool:
        if self.node_type == 'boolean_nullary_observable':
            return observables['boolean'][self.value]
        if self.terminal == 'boolean_nullary_random:uniform':
            return random.randint(0, 1) == 1
        return self.value == 'true'

    @property
    def formula(self) -> str:
        return self.value

    @property
    def is_static(self) -> bool:
        if self.node_type in ['boolean_nullary_observable', 'boolean_nullary_random']:
            return False
        return True


class BooleanUnary(Tree):
    def evaluate(self, observables=None) -> bool:
        if self.value == 'not':
            return not self.children[0].evaluate(observables)

    @property
    def formula(self) -> str:
        return f'{self.value.upper()}({self.children[0].formula})'


class BooleanUnaryNum(Tree):
    def _continue_deserialization(self, recipe):
        child, recipe = self.create(recipe)
        self.children.append(child)
        return recipe

    def evaluate(self, observables=None) -> bool:
        if self.value == 'truthy':
            return self.children[0].evaluate(observables) != 0

    @property
    def formula(self) -> str:
        return f'{self.value.upper()}({self.children[0].formula})'


class BooleanBinary(Tree):
    def evaluate(self, observables=None) -> bool:
        first_operand = self.children[0].evaluate(observables)
        second_operand = self.children[1].evaluate(observables)

        if self.value == 'and':
            return first_operand and second_operand
        if self.value == 'or':
            return first_operand or second_operand

    @property
    def formula(self) -> str:
        return f"({self.children[0].formula} {self.value.upper()} {self.children[1].formula})"


class BooleanBinaryNum(Tree):
    def evaluate(self, observables=None) -> bool:
        first_operand = self.children[0].evaluate(observables)
        second_operand = self.children[1].evaluate(observables)

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
        return f"({self.children[0].formula} {self.value.upper()} {self.children[1].formula})"


class BooleanTernary(Tree):
    def evaluate(self, observables=None) -> bool:
        if self.children[0].evaluate(observables):
            return self.children[1].evaluate(observables)
        return self.children[2].evaluate(observables)

    @property
    def formula(self) -> str:
        return f"IF({self.children[0].formula} ; {self.children[1].formula} ; {self.children[2].formula})"
