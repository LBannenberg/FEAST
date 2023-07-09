import feast.tree as tree
from metaheuristics.tworate import TwoRateEa
import common

# Logger settings
EXPERIMENT_NAME = common.parameters['OUTPUT_DIR'] + 'experiment_02'
ALGORITHM_NAME = 'fixed_two-rate'

sentence = 'numeric_nullary_observable:rate'
root = tree.create(sentence)

problem = common.get_fresh_problem()

logger = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
problem.attach_logger(logger)

for i in range(5):
    inner_heuristic = TwoRateEa(common.parameters['CHILD_POP_SIZE'])
    inner_heuristic.configure(problem, common.parameters['INNER_BUDGET'], {'adaptation': root.evaluate})
    inner_heuristic.initialize_population()
    y_best, x_best, problem = inner_heuristic.run()
    print(f"result: {y_best} as {x_best} using {problem.state.evaluations} evaluations")
    problem.reset()
