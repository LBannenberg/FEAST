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
        # TODO: novelty constraint


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
                success, child = self._expand_leaf_aggressively(child)
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
        for chosen_node_index in random_order:
            terminal = candidates[chosen_node_index]['terminal']
            serial_index = candidates[chosen_node_index]['serial_index']
            alternative_terminal: Union[None, str] = self.grammar.get_alternative_terminal(terminal)
            if alternative_terminal is not None:
                new_recipe = self._replace_subrecipe(child.serialize(), serial_index, terminal, alternative_terminal)
                return True, tree.create(new_recipe)
        return False, child

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
                    main_recipe=child.serialize(),
                    serial_index=chosen_node['serial_index'],
                    old_subrecipe=chosen_node['recipe'],
                    new_subrecipe=candidate_child_information['recipe']
                )
                # return a fresh child based on the new recipe
                return True, tree.create(new_recipe)
        return False, child

    def _expand_leaf_aggressively(self, child: tree.Tree) -> Tuple[bool, tree.Tree]:
        indexed_nodes = child.collect_index()
        candidates = dict(filter(lambda item: item[1]['min_leaf_dist'] == 0, indexed_nodes.items()))
        choice_index = random.sample(candidates.keys(), 1)[0]
        chosen_node = candidates[choice_index]
        new_starting_symbol = self.grammar.get_reduction_to_type_non_terminal(chosen_node['terminal'])
        new_subtree_recipe = self.grammar.produce_random_sentence(new_starting_symbol, minimum_length=2)
        new_recipe = self._replace_subrecipe(
            child.serialize(),
            chosen_node['serial_index'],
            chosen_node['recipe'],
            new_subtree_recipe
        )
        return True, tree.create(new_recipe)

    def _crossover(self, parent1: tree.Tree, parent2: tree.Tree) -> Tuple[bool, tree.Tree]:
        p1_metadata = parent1.collect_index()
        p2_metadata = parent2.collect_index()

        # Figure out which types are available for crossover (only bool, only num, or both)
        p2_possible_types = set(node['return_type'] for node in p2_metadata.values())

        # Narrow down p1 candidate nodes by p2 possible return types
        p1_candidates = dict(filter(lambda item: item[1]['return_type'] in p2_possible_types, p1_metadata.items()))

        # Chose a p1 node
        p1_choice_index = random.sample(p1_candidates.keys(), 1)[0]
        p1_chosen_node = p1_candidates[p1_choice_index]

        # Narrow down p2 candidate nodes by return type of chosen p1 node
        p2_candidates = dict(filter(lambda item: item[1]['return_type'] == p1_chosen_node['return_type'], p2_metadata.items()))

        # Pick a p2 node
        p2_choice_index = random.sample(p2_candidates.keys(), 1)[0]
        p2_chosen_node = p2_candidates[p2_choice_index]

        # Cross over a recipe segment from p2 to p1's recipe
        new_recipe = self._replace_subrecipe(
            main_recipe=parent1.serialize(),
            serial_index=p1_chosen_node['serial_index'],
            old_subrecipe=p1_chosen_node['recipe'],
            new_subrecipe=p2_chosen_node['recipe'],
        )
        return True, tree.create(new_recipe)

    @staticmethod
    def _replace_subrecipe(main_recipe: str, serial_index: int, old_subrecipe: str, new_subrecipe: str) -> str:
        if serial_index == 0:
            return main_recipe.replace(old_subrecipe, new_subrecipe, 1)

        split = main_recipe.split('|')
        left = '|'.join(split[:serial_index])
        right = '|'.join(split[serial_index:])
        return '|'.join([left, right.replace(old_subrecipe, new_subrecipe, 1)])


