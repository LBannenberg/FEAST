import feast.tree as tree
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

f = common.get_fresh_problem()
l = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
f.attach_logger(l)
inner_heuristic = common.get_fresh_inner_heuristic(f)
inner_heuristic.inject_function(root.evaluate)
y_best, x_best, f = inner_heuristic.run()
print(f"result: {y_best} as {x_best} using {f.state.evaluations} evaluations")
