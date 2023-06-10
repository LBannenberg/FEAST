import feast.tree as tree
import common

# Logger settings
EXPERIMENT_NAME = common.parameters['OUTPUT_DIR'] + 'experiment_01'
ALGORITHM_NAME = 'original_two-rate'

sentence = '|'.join([
    'if:numeric|boolean_expression:<=',
    'numeric:uniform',
    'if:numeric|boolean_observable:best_child_is_low|numeric:0.75|numeric:0.25',
    'numeric_expression:max', 'numeric_expression:/', 'numeric_observable:rate', 'numeric:2', 'numeric:2',
    'numeric_expression:min', 'numeric_expression:*', 'numeric_observable:rate', 'numeric:2', 'numeric_expression:/',
    'numeric_observable:dimension', 'numeric:4',
])
root = tree.create(sentence)


if __name__ == '__main__':
    f = common.get_fresh_problem()
    l = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
    f.attach_logger(l)
    inner_heuristic = common.get_fresh_inner_heuristic(f)
    inner_heuristic.adaptation_function = root.evaluate
    y_best, x_best, f = inner_heuristic.run()
    print(f"result: {y_best} as {x_best} using {f.state.evaluations} evaluations")
