from feast.tree.base import Tree


class Numeric(Tree):
    node_type = 'numeric'

    def inflate(self, recipe):
        return recipe

    def evaluate(self, observables=None) -> float:
        if self.debug:
            print(f"{self._indent()}[constant] : {self.value}")
        return float(self.value)


class NumericExpression(Tree):
    node_type = 'numeric_expression'

    def inflate(self, recipe):
        if self.value in ['negative', 'numeric']:  # unary operators
            child, recipe = self._create(recipe)
            self.children.append(child)
        if self.value in ['+', '-', '*', '/', '%', '^']:  # binary operators
            child, recipe = self._create(recipe)
            self.children.append(child)
            child, recipe = self._create(recipe)
            self.children.append(child)
        return recipe

    def evaluate(self, observables=None) -> float:
        first_operand = self.children[0].evaluate(observables)
        if self.debug and self.value in ['negative']:  # debug only negations, not bare numbers
            print(f"{self._indent()}numeric_expression : {self.value} {first_operand}")

        if self.value == 'negative':
            return -1 * first_operand
        if self.value == 'numeric':
            return first_operand

        second_operand = self.children[1].evaluate(observables)
        if self.debug:
            print(f"{self._indent()}numeric_expression : {first_operand} {self.value} {second_operand}")

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


class NumericObservable(Tree):
    node_type = 'numeric_observable'

    def inflate(self, recipe):
        return recipe

    def evaluate(self, observables=None) -> float:
        if self.debug:
            print(f"{self._indent()}[observable : {self.value}]: {float(observables[self.value])}")
        return float(observables[self.value])
