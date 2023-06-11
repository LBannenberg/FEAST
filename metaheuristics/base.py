from abc import ABC, abstractmethod
from ioh import ProblemType


class Heuristic(ABC):
    def __init__(self, problem: ProblemType, dimension: int, budget: int):
        self.problem = problem
        self.dimension = dimension
        self.budget = budget
        self.best = None
        self.current = None
        self.f_best = None
        self.f_current = None

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def inject_function(self, function):
        pass
