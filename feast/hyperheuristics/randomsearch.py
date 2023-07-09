from ioh import ProblemType

import feast.tree as tree
from feast.grammar import Grammar
from feast.hyperheuristics.base import HyperHeuristic


class RandomSearch(HyperHeuristic):
    def __init__(self,
                 grammar: Grammar,
                 starting_symbol: str,
                 problem: ProblemType,
                 build_inner_heuristic,
                 outer_budget: int,
                 trials_per_evaluation: int,
                 must_observe=None,
                 cache_phenotype_evaluations: bool = True,
                 soft_limit=3
                 ):
        super().__init__(
            grammar=grammar,
            starting_symbol=starting_symbol,
            problem=problem,
            build_inner_heuristic=build_inner_heuristic,
            outer_budget=outer_budget,
            trials_per_evaluation=trials_per_evaluation,
            parent_population_size=1,
            child_population_size=1,
            survival='plus',
            cache_phenotype_evaluations=cache_phenotype_evaluations
        )
        self.soft_limit = soft_limit
        self.must_observe = must_observe

    def initialize_population(self):
        while True:
            recipe = self.grammar.produce_random_sentence(soft_limit=self.soft_limit, starting_symbol='NUM')
            root = tree.create(recipe)
            if self._validate(root, False):
                self.parent_population = [root]
                self.parent_population_fitness = [self._evaluate(root)]
                return

    def _generate_child(self):
        while True:
            recipe = self.grammar.produce_random_sentence(soft_limit=self.soft_limit, starting_symbol='NUM')
            root = tree.create(recipe)
            if self._validate(root, False):
                return root

    def _validate(self, individual: tree.Tree, strict: bool) -> bool:
        if self.must_observe and type(self.must_observe) is list:
            serialized = individual.serialize()
            for terminal in self.must_observe:
                if terminal not in serialized:
                    return False
        return True
