import feast.tree as tree
import math
import common
import numpy as np

# Logger settings
EXPERIMENT_NAME = common.parameters['OUTPUT_DIR'] + 'experiment_03'
ALGORITHM_NAME = 'random-search-1+1'


grammar = common.get_grammar()
lowest_evaluations = math.inf
best_recipe = None

# Train
print('training', end='')
for i in range(common.parameters['OUTER_BUDGET']):
    print('.', end='')
    recipe = grammar.produce_random_sentence(soft_limit=5, starting_symbol='NUM')
    root = tree.create(recipe)

    performance = []
    for i in range(common.parameters['OUTER_TRIALS']):
        f = common.get_fresh_problem()
        inner_heuristic = common.get_fresh_inner_heuristic(f)
        inner_heuristic.inject_function(root.evaluate)
        y_best, x_best, f = inner_heuristic.run()
        performance.append(f.state.evaluations)
    mean = np.mean(performance)
    if mean < lowest_evaluations:
        lowest_evaluations = mean
        best_recipe = recipe
print('finished')

# Validate on end result
root = tree.create(best_recipe)

for i in range(5):
    f = common.get_fresh_problem()
    l = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
    f.attach_logger(l)

    inner_heuristic = common.get_fresh_inner_heuristic(f)
    inner_heuristic.inject_function(root.evaluate)
    y_best, x_best, f = inner_heuristic.run()
    print(f"result: {y_best} as {x_best} using {f.state.evaluations} evaluations")
