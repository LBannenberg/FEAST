import feast.tree as tree
import common

# Logger settings
EXPERIMENT_NAME = common.parameters['OUTPUT_DIR'] + 'experiment_01'
ALGORITHM_NAME = 'fixed_two-rate'

sentence = 'numeric_observable:rate'
root = tree.create(sentence)

f = common.get_fresh_problem()
l = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
f.attach_logger(l)
inner_heuristic = common.get_fresh_inner_heuristic(f)
inner_heuristic.inject_function(root.evaluate)
y_best, x_best, f = inner_heuristic.run()
print(f"result: {y_best} as {x_best} using {f.state.evaluations} evaluations")
