import feast.tree as tree
from metaheuristics.tworate import TwoRateEa
import math
import common
import numpy as np

# Logger settings
EXPERIMENT_NAME = common.parameters['OUTPUT_DIR'] + 'experiment_03'
ALGORITHM_NAME = 'random-search-1+1'

grammar = common.get_grammar()
problem = common.get_fresh_problem()
best_score = -math.inf
best_recipe = None

# Train
print('training')
for i in range(1, common.parameters['OUTER_BUDGET']+1):
    print('.', end='')
    if not i % 100:
        print(f' {best_score}')
    recipe = grammar.produce_random_sentence(soft_limit=5, starting_symbol='NUM')
    root = tree.create(recipe)

    # Evaluate the new candidate
    performance = []
    for i in range(common.parameters['OUTER_TRIALS']):
        inner_heuristic = TwoRateEa(common.parameters['CHILD_POP_SIZE'])
        inner_heuristic.configure(problem, common.parameters['INNER_BUDGET'], {'adaptation': root.evaluate})
        inner_heuristic.initialize_population()
        y_best, x_best, f = inner_heuristic.run()
        leftover_budget = common.parameters['INNER_BUDGET'] - f.state.evaluations
        leftover_ratio = leftover_budget / common.parameters['INNER_BUDGET']
        score = y_best + leftover_ratio  # leftover budget ratio is a tiebreaker
        performance.append(score)
        problem.reset()
    mean = np.mean(performance)
    if mean > best_score:
        best_score = mean
        best_recipe = recipe

print('finished')

# Validate on end result
root = tree.create(best_recipe)

problem.reset()
logger = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
problem.attach_logger(logger)

for i in range(5):
    inner_heuristic = common.build_two_rate_ea(problem, root.evaluate)
    y_best, x_best, problem = inner_heuristic.run()
    print(f"result: {y_best} as {x_best} using {problem.state.evaluations} evaluations")
    problem.reset()
