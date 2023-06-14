import random
import feast.tree as tree
import numpy as np
from feast import HyperHeuristic


class Topiary(HyperHeuristic):
    def __init__(
            self,
            grammar,
            starting_symbol: str,
            get_fresh_problem,
            get_fresh_inner_heuristic,
            outer_budget: int,
            parent_population_size: int,
            child_population_size: int,
            trials_per_evaluation: int,
            survival: str = 'comma',
            enforce_unique_phenotypes=False,
            must_observe=None,
            random_seed=None
    ):
        super().__init__(
            grammar,
            starting_symbol,
            get_fresh_problem,
            get_fresh_inner_heuristic,
            outer_budget,
            trials_per_evaluation,
            parent_population_size,
            child_population_size,
            survival,
            random_seed,
            must_observe
        )

        self.enforce_unique_phenotypes = enforce_unique_phenotypes
        self.unique_phenotypes = set()

    def initialize_population(self):
        # TODO: make this more generic so it can be moved into the abstract class
        while len(self.parent_population) < self.parent_population_size:
            parent = self.grammar.produce_random_sentence(starting_symbol=self.starting_symbol)
            if self._validate(parent):
                self.parent_population.append(parent)
                self.unique_phenotypes.add(parent.serialize())

            # Evaluate the parent population
            self.parent_population_fitness = [self._evaluate(parent) for parent in self.parent_population]
            self.parent_population, self.parent_population_fitness = self._sort_by_fitness(
                self.parent_population, self.parent_population_fitness)

    def _validate(self, individual, strict=True):
        if self.must_observe and type(self.must_observe) is list:
            serialized = individual.serialize()
            for terminal in self.must_observe:
                if terminal not in serialized:
                    return False

        if not strict:
            return True

        # TODO: strict checks

        return True

    def _generate_child(self):
        pass
