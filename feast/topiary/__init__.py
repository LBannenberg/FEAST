import random
import feast.tree as tree
import numpy as np
from feast import HyperHeuristic
import json
from feast.grammar import Grammar


class Topiary(HyperHeuristic):
    def __init__(
            self,
            grammar: Grammar,
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
        # TODO: make this more generic, so it can be moved into the abstract class
        print("Initializing population...")
        while len(self.parent_population) < self.parent_population_size:
            parent = tree.create(self.grammar.produce_random_sentence(starting_symbol=self.starting_symbol, soft_limit=5))
            if self._validate(parent):
                self.parent_population.append(parent)
                self.unique_phenotypes.add(parent.serialize())

        # Evaluate the parent population
        print("Evaluating initial population...")
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

    def _generate_child(self) -> tree.Tree:
        parent1, parent2 = random.sample(self.parent_population, 2)
        child = tree.create(parent1.serialize())
        roll = random.randint(0, 3)
        if roll == 0:
            return self._crossover(child, parent2)
        if roll == 1:
            return self._switch_leaf(child)
        if roll == 2:
            return self._expand_leaf(child)
        if roll == 3:
            return self._trim_subtree(child)
        if roll == 4:
            return self._change_internal_node(child)

    def _crossover(self, child, parent2) -> tree.Tree:
        return child

    def _expand_leaf(self, child) -> tree.Tree:
        return child

    def _switch_leaf(self, child) -> tree.Tree:
        index = child.collect_index()
        leaves = self._filter_leaves(index)
        chosen_node_index = random.sample(leaves.keys(), 1)
        chosen_node = leaves[chosen_node_index]
        alternative_value = self.grammar.get_alternative_for_terminal(chosen_node['recipe'])
        child.alter_node_value(chosen_node_index, alternative_value)
        return child

    def _trim_subtree(self, child):
        return child

    def _change_internal_node(self, child):
        return child

    @staticmethod
    def _filter_leaves(indexed_nodes):
        # item is a (key, value) tuple
        return dict(filter(lambda item: item[1]['min_leaf_dist'] == 0, indexed_nodes.items()))
