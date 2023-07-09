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

common.benchmark(common.build_two_rate_ea, problem, root.evaluate)
