import random

from ioh import ProblemType

import feast.tree as tree
import numpy as np
from feast import HyperHeuristic


class GE(HyperHeuristic):
    def __init__(
            self,
            grammar,
            starting_symbol: str,
            problem: ProblemType,
            get_fresh_inner_heuristic,
            outer_budget: int,
            parent_population_size: int,
            child_population_size: int,
            mutation_probability: float,
            crossover_probability: float,
            trials_per_evaluation: int,
            genome_length: int = 1000,
            codon_size: int = 10000,
            enforce_unique_genotypes=False,
            enforce_unique_coding_genotypes=False,
            enforce_unique_phenotypes=False,
            survival: str = 'comma',
            random_seed=None,
            must_observe=None
    ):
        super().__init__(
            grammar,
            starting_symbol,
            problem,
            get_fresh_inner_heuristic,
            outer_budget,
            trials_per_evaluation,
            parent_population_size,
            child_population_size,
            survival,
            random_seed,
            must_observe
        )
        self.genotypes = set()
        self.coding_genotypes = set()
        self.phenotypes = set()
        self.crossover_probability: float = crossover_probability
        self.mutation_probability: float = mutation_probability
        self.genome_length: int = genome_length
        self.codon_size: int = codon_size
        self.enforce_unique_genotypes = enforce_unique_genotypes
        self.enforce_unique_coding_genotypes = enforce_unique_coding_genotypes
        self.enforce_unique_phenotypes = enforce_unique_phenotypes

    def initialize_population(self):
        # Generate a parent population, subject to uniqueness constraints

        while len(self.parent_population) < self.parent_population_size:
            parent = [random.randint(0, self.codon_size - 1) for i in range(self.genome_length)]
            if self._validate(parent):
                self.parent_population.append(parent)

        # Evaluate the parent population
        self.parent_population_fitness = [self._evaluate(parent) for parent in self.parent_population]
        self.parent_population, self.parent_population_fitness = self._sort_by_fitness(
            self.parent_population, self.parent_population_fitness)

    def get_individual(self, index: int):
        recipe = self.get_recipe(index)
        return self._recipe_to_root(recipe)

    @staticmethod
    def _recipe_to_root(recipe):
        return tree.create(recipe)

    def get_recipe(self, index: int):
        genome = self.parent_population[index]
        return self._genome_to_recipe(genome)

    def _genome_to_recipe(self, genome):
        recipe = self.grammar.get_sentence_from_genome(genome, starting_symbol=self.starting_symbol)
        return recipe

    def _evaluate(self, individual):
        root = self._recipe_to_root(self._genome_to_recipe(individual))
        return super()._evaluate(root)

    def _validate(self, genome, strict=True):
        try:
            recipe = self._genome_to_recipe(genome)
        except ValueError as e:
            return False

        try:
            root = self._recipe_to_root(recipe)
        except ValueError as e:
            print(f"ValueError: {recipe}")
            return False
        except AttributeError as e:
            print(f"AttributeError: {recipe}")
            return False

        if self.must_observe and type(self.must_observe) is list:
            for terminal in self.must_observe:
                if terminal not in recipe:
                    return False

        if not strict:
            return True

        if self.enforce_unique_coding_genotypes:
            coding_length = self._get_coding_length(genome)
            signature = '.'.join([str(i) for i in genome[:coding_length]])
            if signature in self.coding_genotypes:
                return False
            self.coding_genotypes.add(signature)

        if self.enforce_unique_genotypes:
            signature = '.'.join([str(i) for i in genome])
            if signature in self.genotypes:
                return False
            self.genotypes.add(signature)

        if self.enforce_unique_phenotypes:
            if recipe in self.phenotypes:
                return False
            self.phenotypes.add(recipe)

        return True

    def _generate_child(self):
        p1 = random.sample(self.parent_population, 1)[0]
        if self.crossover_probability > random.uniform(0, 1):
            p2 = p1
            while p2 == p1:
                p2 = random.sample(self.parent_population, 1)[0]
            return self._crossover(p1, p2)
        else:
            return self._mutation(p1)

    def _crossover(self, p1, p2):
        # Crossover at a point that is within the coding length of both parents
        coding_length_p1 = self._get_coding_length(p1)
        coding_length_p2 = self._get_coding_length(p2)
        point = random.randint(0, min(coding_length_p1, coding_length_p2))
        return p1[:point] + p2[point:]

    def _mutation(self, p1):
        coding_length_p1 = self._get_coding_length(p1)
        child = p1.copy()
        point = random.randint(0, coding_length_p1)
        child[point] = random.randint(0, self.codon_size - 1)
        return child

    def _get_coding_length(self, genome):
        return self.grammar.get_genome_coding_length(genome, self.starting_symbol)
