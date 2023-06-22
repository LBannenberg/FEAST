from feast.tree.base import Tree
import random


class NumericNullary(Tree):
    def evaluate(self, observables=None) -> float:
        if self.node_type == 'numeric_nullary_observable':
            return observables['numeric'][self.value]
        if self.terminal == 'numeric_nullary_random:uniform':
            return random.uniform(0, 1)
        return float(self.value)

    @property
    def formula(self) -> str:
        return self.value

    @property
    def is_static(self) -> bool:
        if self.node_type in ['numeric_observable', 'numeric_random']:
            return False
        return True


class NumericUnary(Tree):
    def evaluate(self, observables=None) -> float:
        if self.value == 'negative':
            return -self.children[0].evaluate(observables)

    @property
    def formula(self) -> str:
        if self.value == 'negative':
            return '-' + self.children[0].formula


class NumericBinary(Tree):
    def evaluate(self, observables=None) -> float:
        first_operand = self.children[0].evaluate(observables)
        second_operand = self.children[1].evaluate(observables)
        try:
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
        if self.value in ['min', 'max']:
            return f"{self.value}({self.children[0].formula}, {self.children[1].formula})"
        return f"({self.children[0].formula} {self.value} {self.children[1].formula})"


class NumericTernary(Tree):
    def evaluate(self, observables=None) -> float:
        if self.children[0].evaluate(observables):
            return self.children[1].evaluate(observables)
        return self.children[2].evaluate(observables)

    @property
    def formula(self) -> str:
        return f"IF({self.children[0].formula} ; {self.children[1].formula} ; {self.children[2].formula})"
