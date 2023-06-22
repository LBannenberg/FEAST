import random
import feast.tree as tree
from feast import HyperHeuristic
import json
from feast.grammar import Grammar
from typing import Union, Tuple


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

    def initialize_population(self) -> None:
        # TODO: make this more generic, so it can be moved into the abstract class
        print("Initializing population...")
        while len(self.parent_population) < self.parent_population_size:
            parent = tree.create(
                self.grammar.produce_random_sentence(starting_symbol=self.starting_symbol, soft_limit=5))
            if self._validate(parent):
                self.parent_population.append(parent)
                self.unique_phenotypes.add(parent.serialize())

        # Evaluate the parent population
        print("Evaluating initial population...")
        self.parent_population_fitness = [self._evaluate(parent) for parent in self.parent_population]
        self.parent_population, self.parent_population_fitness = self._sort_by_fitness(
            self.parent_population, self.parent_population_fitness)

    def _validate(self, individual: tree.Tree, strict=True) -> bool:
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
        success = False

        # Shuffle the variations that will be tried
        options = list(range(5))
        random.shuffle(options)

        for option in options:
            if success:  # stop as soon as a variation succeeds
                break
            if option == 0:
                success, child = self._switch_internal_node(child)
            if option == 1:
                success, child = self._switch_leaf_node(child)
            if option == 2:
                success, child = self._trim_subtree(child)
            if option == 3:
                success, child = self._expand_leaf(child)
            if option == 4:
                success, child = self._crossover(child, parent2)

        if not success:
            print(f"Could not generate a variant child.")
            print(child)
            exit(1)

        return child

    def _switch_leaf_node(self, child: tree.Tree) -> Tuple[bool, tree.Tree]:
        indexed_nodes = child.collect_index()
        candidates = dict(filter(lambda item: item[1]['min_leaf_dist'] == 0, indexed_nodes.items()))
        if len(candidates) == 1:  # single-node tree
            return False, child
        return self._switch_node(child, candidates)

    def _switch_internal_node(self, child: tree.Tree) -> Tuple[bool, tree.Tree]:
        indexed_nodes = child.collect_index()
        candidates = dict(filter(lambda item: item[1]['min_leaf_dist'] > 0, indexed_nodes.items()))
        if not len(candidates):
            return False, child
        return self._switch_node(child, candidates)

    def _switch_node(self, child: tree.Tree, candidates: dict) -> Tuple[bool, tree.Tree]:
        random_order = list(candidates.keys())
        random.shuffle(random_order)
        alternative_terminal: Union[bool, str] = False
        chosen_node_index = None
        for chosen_node_index in random_order:
            terminal = candidates[chosen_node_index]['terminal']
            alternative_terminal = self.grammar.get_alternative_terminal(terminal)
            if alternative_terminal:
                break
        if not alternative_terminal:
            return False, child
        new_value = alternative_terminal.split(':')[1]
        child.alter_node_value(chosen_node_index, new_value)
        return True, child

    def _trim_subtree(self, child: tree.Tree) -> Tuple[bool, tree.Tree]:
        indexed_nodes = child.collect_index()
        # Filter for subtrees that have a leaf as direct child
        candidates = dict(filter(lambda item: item[1]['min_leaf_dist'] == 1, indexed_nodes.items()))
        if not len(candidates):
            return False, child

        # select a subtree
        random_order = list(candidates.keys())
        random.shuffle(random_order)
        for chosen_node_index in random_order:
            chosen_node = candidates[chosen_node_index]
            chosen_node_return_type = self.grammar.get_reduction_to_type_non_terminal(chosen_node['terminal'])
            candidate_children = list(range(chosen_node['num_children']))
            random.shuffle(candidate_children)
            for candidate_child_index in candidate_children:
                candidate_child_information = indexed_nodes[f"{chosen_node_index}.{candidate_child_index}"]

                # test if the child's type is the same as the parent
                candidate_child_return_type = self.grammar.get_reduction_to_type_non_terminal(candidate_child_information['terminal'])
                if candidate_child_return_type != chosen_node_return_type:
                    continue  # the candidate child doesn't have the same return type as the parent so cannot succeed

                # replace the parent's part of the overall recipe with that of the child
                new_recipe = self._replace_subrecipe(
                    old_recipe=child.serialize(),
                    serial_index=chosen_node['serial_index'],
                    find=chosen_node['recipe'],
                    replacement=candidate_child_information['recipe']
                )
                # return a fresh child based on the new recipe
                return True, tree.create(new_recipe)
        return False, child

    def _expand_leaf(self, child: tree.Tree) -> Tuple[bool, tree.Tree]:
        # select a leaf
        # select a branching operation
        # also produce branches
        return False, child

    def _crossover(self, child: tree.Tree, parent2: tree.Tree) -> Tuple[bool, tree.Tree]:
        # pick a node in the child
        # pick a node of the same type in parent2
        return False, child

    @staticmethod
    def _replace_subrecipe(old_recipe: str, serial_index: int, find: str, replacement: str) -> str:
        split = old_recipe.split('|')
        left = '|'.join(split[:serial_index])
        right = '|'.join(split[serial_index:])
        return '|'.join([left, right.replace(find, replacement, 1)])


