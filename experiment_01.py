import feast.tree as tree
from metaheuristics.tworate import TwoRateEa
import common

# Logger settings
EXPERIMENT_NAME = common.parameters['OUTPUT_DIR'] + 'experiment_01'
ALGORITHM_NAME = 'original_two-rate'

sentence = '|'.join([
    'numeric_ternary:if',
        'boolean_binary_num:<=',  # rand() <= s
            'numeric_nullary_random:uniform',
            'numeric_ternary:if',  # s = 3/4 if best_child_is_low else 1/4
                'boolean_nullary_observable:best_child_is_low',
                    'numeric_nullary:0.75',
                    'numeric_nullary:0.25',
        'numeric_binary:max',  # max(rate/2, 2)
            'numeric_binary:/',
                'numeric_nullary_observable:rate',
                'numeric_nullary:2',
            'numeric_nullary:2',
        'numeric_binary:min',  # min(rate*2, dimension/4)
            'numeric_binary:*',
                'numeric_nullary_observable:rate',
                'numeric_nullary:2',
            'numeric_binary:/',
                'numeric_nullary_observable:dimension',
                'numeric_nullary:4',
])
root = tree.create(sentence)

problem = common.get_fresh_problem()

logger = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
problem.attach_logger(logger)

common.benchmark(common.build_two_rate_ea, problem, root.evaluate)
