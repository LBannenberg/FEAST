from .base import Heuristic
import random
import math


class TwoRateEa(Heuristic):
    def __init__(self, problem, dimension: int, budget: int, child_pop_size: int):
        super().__init__(problem, dimension, budget)
        self.child_pop = []
        self.rate = 2
        self.child_pop_size = child_pop_size
        self.initialize()

    def initialize(self):
        # generate one individual
        self.best = [random.randint(0, 1) for i in range(self.dimension)]
        self.f_best = self.problem(self.best)

    def mutation(self, probability_per_bit):
        mutations = []
        while sum(mutations) < 1:
            mutations = [int(random.random() <= probability_per_bit) for i in range(self.dimension)]
        return [abs(x - y) for x, y in zip(self.best, mutations)]

    def run(self):
        epoch = 0
        while self.problem.state.evaluations < self.budget and self.f_best < int(self.problem.optimum.y):
            epoch += 1
            child_population_size = min(self.child_pop_size, (self.budget - self.problem.state.evaluations))
            current_best = None
            f_current_best = 0
            best_child_is_low = None

            p = self.rate / (2 * self.dimension)
            for i in range(math.ceil(child_population_size / 2)):
                child = self.mutation(p)
                f = self.problem(child)
                if f >= f_current_best:
                    current_best = child
                    f_current_best = f
                    best_child_is_low = True

            p = 2 * self.rate / self.dimension
            for i in range(math.floor(child_population_size / 2)):
                child = self.mutation(p)
                f = self.problem(child)
                if f >= f_current_best:
                    current_best = child
                    f_current_best = f
                    best_child_is_low = False

            if f_current_best > self.f_best:
                self.best = current_best
                self.f_best = f_current_best

            self._adapt_rate(best_child_is_low)
        return [int(self.f_best), self.best, self.problem]

    def _adapt_rate(self, best_child_is_low):
        observables = {
            'boolean': {'best_child_is_low': best_child_is_low},
            'numeric': {'rate': self.rate, 'dimension': self.dimension}
        }
        self.rate = round(min(max(self.adaptation_function(observables), 0.001), 3), 10**10)

    def inject_function(self, function):
        self.adaptation_function = function

    @staticmethod
    def _adaptation_function(observables):
        return observables['numeric']['rate']
