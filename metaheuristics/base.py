from typing import Dict, Callable
from abc import ABC, abstractmethod
from ioh import ProblemType


class Heuristic(ABC):
    def __init__(self):
        self.problem = None
        self.dimension = 0
        self.budget = 0
        self.best = None
        self.current = None
        self.f_best = None
        self.f_current = None

    @abstractmethod
    def configure(self, problem: ProblemType, budget: int, injections: Dict[str, Callable]):
        pass

    @abstractmethod
    def initialize_population(self):
        pass

    @abstractmethod
    def run(self):
        pass

