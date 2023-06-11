import common
from feast.ge import GE

# Logger settings
EXPERIMENT_NAME = common.parameters['OUTPUT_DIR'] + 'experiment_04'
ALGORITHM_NAME = 'classic-GE'

ge = GE(
    common.get_grammar(),
    'NUMERIC_EXPRESSION',
    common.get_fresh_problem,
    common.get_fresh_inner_heuristic,
    common.parameters['OUTER_BUDGET'],
    trials_per_evaluation=common.parameters['OUTER_TRIALS'],
    parent_population_size=5,
    child_population_size=15,
    mutation_probability=0.1,
    crossover_probability=0.5,
    genome_length=50,
    enforce_unique_genotypes=True,
    enforce_unique_phenotypes=True,
    enforce_unique_coding_genotypes=True,
    survival='plus'
)
ge.initialize_population()
ge.run()

print("Formulas in the final population:")
grammar = common.get_grammar()
for i in range(ge.parent_population_size):
    print(f"recipe: {ge.get_recipe(i)}")
    fitness = ge.parent_population_fitness[i]
    root = ge.get_individual(i)
    print(f"[{fitness}]: {root.formula}")

root = ge.get_individual(0)
print(f"Best Formula: {root.formula}")

f = common.get_fresh_problem()
l = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
f.attach_logger(l)

inner_heuristic = common.get_fresh_inner_heuristic(f)
inner_heuristic.adaptation_function = root.evaluate
y_best, x_best, f = inner_heuristic.run()
print(f"result: {y_best} as {x_best} using {f.state.evaluations} evaluations")
