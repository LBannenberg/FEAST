import feast.tree as tree
from metaheuristics.tworate import TwoRateEa
import common

# Logger settings
EXPERIMENT_NAME = common.parameters['OUTPUT_DIR'] + 'experiment_01'
ALGORITHM_NAME = 'original_two-rate'

sentence = '|'.join([
    'numeric_ternary:if|boolean_binary_num:<=',
    'numeric_nullary_random:uniform',
    'numeric_ternary:if|boolean_nullary_observable:best_child_is_low|numeric_nullary:0.75|numeric_nullary:0.25',
    'numeric_binary:max', 'numeric_binary:/', 'numeric_nullary_observable:rate', 'numeric_nullary:2', 'numeric_nullary:2',
    'numeric_binary:min', 'numeric_binary:*', 'numeric_nullary_observable:rate', 'numeric_nullary:2', 'numeric_binary:/',
    'numeric_nullary_observable:dimension', 'numeric_nullary:4',
])
root = tree.create(sentence)

problem = common.get_fresh_problem()

logger = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
problem.attach_logger(logger)

for i in range(5):
    inner_heuristic = TwoRateEa(common.parameters['CHILD_POP_SIZE'])
    inner_heuristic.configure(problem, common.parameters['INNER_BUDGET'], {'adaptation': root.evaluate})
    logger.add_run_attributes(inner_heuristic, ['rate'])
    inner_heuristic.initialize_population()
    y_best, x_best, problem = inner_heuristic.run()
    print(f"result: {y_best} as {x_best} using {problem.state.evaluations} evaluations")
    problem.reset()
