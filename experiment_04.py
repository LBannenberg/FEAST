import feast.tree as tree
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
    parent_population_size=10,
    child_population_size=10,
    mutation_probability=0.1,
    crossover_probability=0.1,
    enforce_unique_coding_genotypes=True
)
ge.initialize_population()
# ge.run()
best_recipe = ge.get_best_recipe()
root = tree.create(best_recipe)
print(root.formula)

f = common.get_fresh_problem()
l = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
f.attach_logger(l)

inner_heuristic = common.get_fresh_inner_heuristic(f)
inner_heuristic.adaptation_function = root.evaluate
y_best, x_best, f = inner_heuristic.run()
print(f"result: {y_best} as {x_best} using {f.state.evaluations} evaluations")
