from feast.tree.base import Tree
import random


class Numeric(Tree):
    node_type = 'numeric'

    def _continue_deserialization(self, recipe):
        return recipe

    def evaluate(self, observables=None) -> float:
        if self.value == 'uniform':
            return random.uniform(0, 1)
        return float(self.value)

    @property
    def formula(self) -> str:
        return str(self.value)

    @property
    def is_static(self) -> bool:
        if self.value == 'uniform':
            return False
        return True


class NumericExpression(Tree):
    node_type = 'numeric_expression'

    def _continue_deserialization(self, recipe):
        if self.value in ['negative', 'numeric']:  # unary operators
            child, recipe = self.create(recipe)
            self.children.append(child)
        if self.value in ['+', '-', '*', '/', '%', '^', 'min', 'max']:  # binary operators
            child, recipe = self.create(recipe)
            self.children.append(child)
            child, recipe = self.create(recipe)
            self.children.append(child)
        return recipe

    def evaluate(self, observables=None) -> float:
        first_operand = self.children[0].evaluate(observables)

        if self.value == 'negative':
            return -1 * first_operand
        if self.value == 'numeric':
            return first_operand

        try:
            second_operand = self.children[1].evaluate(observables)

            if self.value == '+':
                return first_operand + second_operand

            if self.value == '-':
                return first_operand - second_operand

            if self.value == '*':
                return first_operand * second_operand

            if self.value == '/':
                return first_operand / second_operand if second_operand != 0 else 0  # protected division

            if self.value == '%':
                return first_operand % second_operand

            if self.value == '^':
                return first_operand ** second_operand

            if self.value == 'min':
                return min(first_operand, second_operand)

            if self.value == 'max':
                return max(first_operand, second_operand)
        except ArithmeticError as e:
            print(f"Error in {first_operand} {self.value} {second_operand}")
            print(e)
            raise e
        except TypeError as e:
            print(f"Error in {first_operand} {self.value} {second_operand}")
            print(e)
            raise e



    @property
    def formula(self) -> str:
        if self.value == 'negative':
            return '-' + self.children[0].formula
        if self.value == 'numeric':
            return self.children[0].formula
        if self.value in ['min', 'max']:
            return f"{self.value}({self.children[0].formula}, {self.children[1].formula})"
        return f"({self.children[0].formula} {self.value} {self.children[1].formula})"


class NumericObservable(Tree):
    node_type = 'numeric_observable'

    def _continue_deserialization(self, recipe):
        return recipe

    def evaluate(self, observables=None) -> float:
        return float(observables['numeric'][self.value])

    @property
    def formula(self) -> str:
        return self.value

    @property
    def is_static(self) -> bool:
        return False
