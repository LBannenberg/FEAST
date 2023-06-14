import random
import feast.tree as tree
import numpy as np


class GE:
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
                 trials_per_evaluation: int,
                 genome_length: int = 1000,
                 codon_size: int = 10000,
                 enforce_unique_genotypes=False,
                 enforce_unique_coding_genotypes=False,
                 enforce_unique_phenotypes=False,
                 survival: str = 'comma',
                 random_seed=None,
                 must_observe=None
                 ):
        self.parent_population = []
        self.parent_population_fitness = []
        self.budget_used = 0
        self.genotypes = set()
        self.coding_genotypes = set()
        self.phenotypes = set()

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
        self.trials_per_evaluation: int = trials_per_evaluation
        self.enforce_unique_genotypes = enforce_unique_genotypes
        self.enforce_unique_coding_genotypes = enforce_unique_coding_genotypes
        self.enforce_unique_phenotypes = enforce_unique_phenotypes
        self.survival = survival
        self.must_observe = must_observe
        if random_seed is not None:
            random.seed(random_seed)

    def initialize_population(self):
        # Generate a parent population, subject to uniqueness constraints

        while len(self.parent_population) < self.parent_population_size:
            parent = [random.randint(0, self.codon_size - 1) for i in range(self.genome_length)]
            if self._validate(parent):
                self.parent_population.append(parent)

        # Evaluate the parent population
        self.parent_population_fitness = [self._evaluate(parent) for parent in self.parent_population]
        self.parent_population, self.parent_population_fitness = self._sort_by_fitness(
            self.parent_population, self.parent_population_fitness)

    def run(self):
        print(f"RUN")
        generation = 0
        while (self.budget_used + self.child_population_size) <= self.outer_budget:
            generation += 1
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

    def get_individual(self, index: int):
        recipe = self.get_recipe(index)
        return self._recipe_to_root(recipe)

    @staticmethod
    def _recipe_to_root(recipe):
        return tree.create(recipe)

    def get_recipe(self, index: int):
        genome = self.parent_population[index]
        return self._genome_to_recipe(genome)

    def _genome_to_recipe(self, genome):
        recipe = self.grammar.get_sentence_from_genome(genome, starting_symbol=self.starting_symbol)
        return recipe

    def _evaluate(self, parent):
        root = self._recipe_to_root(self._genome_to_recipe(parent))
        performance = []
        for i in range(self.trials_per_evaluation):
            f = self.get_fresh_problem()
            inner_heuristic = self.get_fresh_inner_heuristic(f)
            inner_heuristic.inject_function(root.evaluate)
            y_best, x_best, f = inner_heuristic.run()
            performance.append(f.state.evaluations)
        self.budget_used += 1
        return np.mean(performance)

    def _validate(self, genome, strict=True):
        try:
            recipe = self._genome_to_recipe(genome)
        except ValueError as e:
            return False

        try:
            root = self._recipe_to_root(recipe)
        except ValueError as e:
            print(f"ValueError: {recipe}")
            return False
        except AttributeError as e:
            print(f"AttributeError: {recipe}")
            return False

        if self.must_observe and type(self.must_observe) is list:
            for terminal in self.must_observe:
                if terminal not in recipe:
                    return False

        if not strict:
            return True

        if self.enforce_unique_coding_genotypes:
            coding_length = self._get_coding_length(genome)
            signature = '.'.join([str(i) for i in genome[:coding_length]])
            if signature in self.coding_genotypes:
                return False
            self.coding_genotypes.add(signature)

        if self.enforce_unique_genotypes:
            signature = '.'.join([str(i) for i in genome])
            if signature in self.genotypes:
                return False
            self.genotypes.add(signature)

        if self.enforce_unique_phenotypes:
            if recipe in self.phenotypes:
                return False
            self.phenotypes.add(recipe)

        return True

    def _generate_child(self):
        p1 = random.sample(self.parent_population, 1)[0]
        if self.crossover_probability > random.uniform(0, 1):
            p2 = p1
            while p2 == p1:
                p2 = random.sample(self.parent_population, 1)[0]
            return self._crossover(p1, p2)
        else:
            return self._mutation(p1)

    def _survival(self, child_population, child_population_fitness):
        if self.survival == 'comma':
            child_population, child_population_fitness = self._sort_by_fitness(child_population, child_population_fitness)
            return child_population[:self.parent_population_size], child_population_fitness[:self.parent_population_size]
        if self.survival == 'plus':
            population = self.parent_population + child_population
            population_fitness = self.parent_population_fitness + child_population_fitness
            population, population_fitness = self._sort_by_fitness(population, population_fitness)
            return population[:self.parent_population_size], population_fitness[:self.parent_population_size]
        raise ValueError(f"Invalid survival rule: {self.survival}")

    @staticmethod
    def _sort_by_fitness(population, fitness):
        tuples = sorted(zip(population, fitness), key=lambda x: x[1])
        return [t[0] for t in tuples], [t[1] for t in tuples]

    def _crossover(self, p1, p2):
        # Crossover at a point that is within the coding length of both parents
        coding_length_p1 = self._get_coding_length(p1)
        coding_length_p2 = self._get_coding_length(p2)
        point = random.randint(0, min(coding_length_p1, coding_length_p2))
        return p1[:point] + p2[point:]

    def _mutation(self, p1):
        coding_length_p1 = self._get_coding_length(p1)
        child = p1.copy()
        point = random.randint(0, coding_length_p1)
        child[point] = random.randint(0, self.codon_size - 1)
        return child

    def _get_coding_length(self, genome):
        return self.grammar.get_genome_coding_length(genome, self.starting_symbol)
