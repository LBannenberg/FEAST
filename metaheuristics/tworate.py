from .base import Heuristic
import random
import math


class TwoRateEa(Heuristic):
    child_pop = []
    rate = 2

    def __init__(self, problem, dimension: int, budget: int, child_pop_size: int, adaptation_function):
        super().__init__(problem, dimension, budget)
        self.child_pop_size = child_pop_size
        self.adaptation_function = adaptation_function
        self.initialize()

    def initialize(self):
        # generate one individual
        self.best = [random.randint(0, 1) for i in range(self.dimension)]
        self.f_best = self.problem(self.best)
        print(
            f"Initialized with {self.best} valued at {self.f_best} with {self.problem.state.evaluations} evaluation(s) used")

    def mutation(self, probability_per_bit):
        mutations = []
        while sum(mutations) < 1:
            mutations = [int(random.random() <= probability_per_bit) for i in range(self.dimension)]
        return [abs(x - y) for x, y in zip(self.best, mutations)]

    def run(self):
        epoch = 0
        target = self.problem.optimum.y - 0.01  # float comparison is not numerically stable
        while self.problem.state.evaluations < self.budget and self.f_best <= target:
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
                print(f"Epoch {epoch} best {self.f_best} < {f_current_best} (target: {self.problem.optimum.y}; evaluations: {self.problem.state.evaluations})")
                self.best = current_best
                self.f_best = f_current_best

            self.rate = self.adaptation_function(best_child_is_low, self.rate, self.dimension)

        print(
            f'Finished. Best individual: {self.best} with value {self.f_best}',
            f' after using {self.problem.state.evaluations}')

        return int(self.f_best)


