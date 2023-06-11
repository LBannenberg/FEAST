import random
import feast.tree as tree
import numpy as np


class GE:
    parent_population = []
    parent_population_fitness = []
    budget_used = 0
    genotypes = set()
    coding_genotypes = set()
    phenotypes = set()

    def __init__(self,
                 grammar,
                 starting_symbol: str,
                 get_fresh_problem,
                 get_fresh_inner_heuristic,
                 outer_budget: int,
                 parent_population_size: int,
                 child_population_size: int,
                 mutation_probability: float,
                 crossover_probability: float,
                 genome_length: int = 1000,
                 codon_size: int = 10000,
                 enforce_unique_genotypes=False,
                 enforce_unique_coding_genotypes=False,
                 enforce_unique_phenotypes=False
                 ):
        self.grammar = grammar
        self.starting_symbol: str = starting_symbol
        self.get_fresh_problem = get_fresh_problem
        self.get_fresh_inner_heuristic = get_fresh_inner_heuristic
        self.outer_budget: int = outer_budget
        self.parent_population_size: int = parent_population_size
        self.child_population_size: int = child_population_size
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
        for parent in self.parent_population:
            self.parent_population_fitness.append(self._evaluate(parent))

    def run(self):
        raise NotImplementedError('TODO')

    def get_best_recipe(self):
        idx = np.asarray(self.parent_population_fitness).argmax()
        genome = self.parent_population[idx]
        return self.grammar.produce_from_genome(genome, starting_symbol=self.starting_symbol)

    def _evaluate(self, parent):
        sentence = self.grammar.produce_from_genome(parent, starting_symbol=self.starting_symbol)
        root = tree.create(sentence)
        f = self.get_fresh_problem()
        inner_heuristic = self.get_fresh_inner_heuristic(f)
        inner_heuristic.adaptation_function = root.evaluate
        y_best, x_best, f = inner_heuristic.run()
        self.budget_used += 1
        return y_best

    def _validate(self, parent):
        sentence = self.grammar.produce_from_genome(parent, starting_symbol=self.starting_symbol)
        if sentence == 'invalid':
            return False
        try:
            tree.create(sentence)
        except ValueError as e:
            print(f"ValueError: {sentence}")
            return False
        except AttributeError as e:
            print(f"AttributeError: {sentence}")
            return False

        if self.enforce_unique_genotypes:
            signature = '.'.join([str(i) for i in parent])
            if signature in self.genotypes:
                return False
            self.genotypes.add(signature)
        if self.enforce_unique_coding_genotypes:
            sentence, coding_length = self.grammar.produce_from_genome(
                parent, starting_symbol=self.starting_symbol, return_coding_length=True
            )
            signature = '.'.join([str(i) for i in parent[:coding_length]])
            if signature in self.coding_genotypes:
                return False
            self.coding_genotypes.add(signature)
        if self.enforce_unique_phenotypes:
            sentence = self.grammar.produce_from_genome(parent, starting_symbol=self.starting_symbol)
            if sentence in self.phenotypes:
                return False
            self.phenotypes.add(sentence)

        return True
