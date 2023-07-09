from abc import ABC, abstractmethod
import numpy as np
import random

from ioh import ProblemType

from feast.grammar import Grammar


class HyperHeuristic(ABC):
    def __init__(self,
                 grammar: Grammar,
                 starting_symbol: str,
                 problem: ProblemType,
                 get_fresh_inner_heuristic,
                 outer_budget: int,
                 trials_per_evaluation: int,
                 parent_population_size: int,
                 child_population_size: int,
                 survival: str = 'comma',
                 random_seed=None,
                 must_observe=None
                 ):

        self.grammar = grammar
        self.starting_symbol: str = starting_symbol

        self.problem = problem
        self.get_fresh_inner_heuristic = get_fresh_inner_heuristic

        self.outer_budget = outer_budget
        self.trials_per_evaluation = trials_per_evaluation

        self.parent_population_size = parent_population_size
        self.child_population_size = child_population_size
        self.survival = survival

        self.must_observe = must_observe

        if random_seed is not None:
            random.seed(random_seed)

        self.budget_used = 0
        self.parent_population_fitness = []
        self.parent_population = []

    @abstractmethod
    def initialize_population(self):
        pass

    def run(self):
        print(f"RUN")
        generation = 0
        while (self.budget_used + self.child_population_size) <= self.outer_budget:
            generation += 1
            if not self.budget_used % 5:
                print(f"  generation {generation} (budget: {self.budget_used}/{self.outer_budget}")
                print(self.parent_population_fitness)

            # Generate new child population
            child_population = []
            attempts = 0
            while len(child_population) < self.child_population_size:
                child = self._generate_child()  # includes variation
                attempts += 1
                strict = attempts < 5
                if self._validate(child, strict=strict):
                    child_population.append(child)
                    attempts = 0

            # Evaluate and survive into next generation
            child_population_fitness = [self._evaluate(child) for child in child_population]
            self.parent_population, self.parent_population_fitness = self._survival(
                child_population, child_population_fitness)

    @abstractmethod
    def _generate_child(self):
        pass

    @abstractmethod
    def _validate(self, child, strict) -> bool:
        pass

    def _evaluate(self, individual):
        performance = []
        for i in range(self.trials_per_evaluation):
            inner_heuristic = self.get_fresh_inner_heuristic(self.problem, individual.evaluate)
            y_best, x_best, f = inner_heuristic.run()

            leftover_budget = inner_heuristic.budget - f.state.evaluations
            leftover_ratio = leftover_budget / inner_heuristic.budget
            score = y_best + leftover_ratio  # leftover budget ratio is a tiebreaker

            performance.append(score)
            self.problem.reset()
        self.budget_used += 1
        return np.mean(performance)

    def _survival(self, child_population, child_population_fitness):
        if self.survival == 'comma':
            child_population, child_population_fitness = self._sort_by_fitness(child_population,
                                                                               child_population_fitness)
            return child_population[:self.parent_population_size], child_population_fitness[
                                                                   :self.parent_population_size]
        if self.survival == 'plus':
            population = self.parent_population + child_population
            population_fitness = self.parent_population_fitness + child_population_fitness
            population, population_fitness = self._sort_by_fitness(population, population_fitness)
            return population[:self.parent_population_size], population_fitness[:self.parent_population_size]
        raise ValueError(f"Invalid survival rule: {self.survival}")

    @staticmethod
    def _sort_by_fitness(population, fitness):
        tuples = sorted(zip(population, fitness), key=lambda x: x[1], reverse=True)
        return [t[0] for t in tuples], [t[1] for t in tuples]
